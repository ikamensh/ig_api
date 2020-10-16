import bisect
import csv
import os
from datetime import datetime
from collections import Counter
from typing import Dict, Iterator, Tuple

from loguru import logger

from ig_api import markets
from ig_api.datasets.resolutions import Resolutions
from ig_api.ig_session import IgSession
from ig_api._config import data_folder

_synth_market_id = markets.MarketId(code=None, name="synthetic_data")


class MarketHistory:
    """ Represents available historic data for a given market.

    Handles:
        1) iteration over the data
        2) saving and loading to .csv file
        3) slicing data based on datetime
    """

    def __init__(self, market: markets.MarketId = _synth_market_id, resolution = Resolutions.HOUR_2):

        assert resolution in Resolutions.__all__

        os.makedirs(os.path.join(data_folder, resolution), exist_ok=True)
        self.csv_path = os.path.join(data_folder, resolution, f"{market.name}.csv")
        self.market = market
        self._data: Dict[datetime, Tuple[float, float, float]] = {}
        self._start = datetime.min
        self._end = datetime.min
        self._keys = None
        self.steps_per_day = None
        self.resolution = resolution
        self._dirty_bit = False

    def compute_start_end_step(self):
        """ Housekeeping - sort the data, find earliest and latest datetime, detect steps per day. """

        srtd = sorted(self._data.items())
        self._start = srtd[0][0] if self._data else None
        self._end = srtd[-1][0] if self._data else None
        self._data = {k: v for k, v in sorted(self._data.items())}
        self._keys = list(self._data.keys())

        if srtd:
            days = [datetime(year=k.year, month=k.month, day=k.day) for k in self._data]
            ctr = Counter(days)
            self.steps_per_day = ctr.most_common()[0][
                1
            ]  # take the most common tuple, second element is the count

        self._dirty_bit = False

    def add_record(self, date_time: datetime, low: float, high: float, delta: float):
        """ Add a single record. """

        self._dirty_bit = True
        self._data[date_time] = low, high, delta

    @staticmethod
    def from_csv(market: markets.MarketId, resolution: str):
        """ Create an MarketHistory based on the data saved in a .csv file.

        Symmetrical with `to_csv` method. """

        result = MarketHistory(market, resolution)

        if not os.path.exists(result.csv_path):
            logger.warning(
                f"File {result.csv_path} doesn't exist - using empty MarketHistory."
            )
            return result

        with open(result.csv_path) as f:
            r = csv.reader(f)
            for t in r:
                timestamp, data = t[0], t[1:]
                low, high, delta = [float(x) for x in data]

                d = datetime.fromisoformat(timestamp)
                result._data[d] = low, high, delta

        result.compute_start_end_step()

        return result

    def to_csv(self):
        """ Dump the data to a local csv file.

        Symmetrical with `from_csv` method. """

        if self._dirty_bit:
            self.compute_start_end_step()

        with open(self.csv_path, "w") as f:
            writer = csv.writer(f, delimiter=",")
            for k, (low, high, delta) in self._data.items():
                low, high, delta = [f"{x:.2f}" for x in [low, high, delta]]
                writer.writerow((k, low, high, delta))

    def update(self, sess: IgSession, start = None, end = None):
        """ Use session to update data to the latest available on the platform. """
        start = start or self.end
        end = end or datetime.now()

        for t, low, high, delta in sess.price_history(
            self.market.code, self.resolution, start=start, end=end
        ):
            self._data[t] = low, high, delta
        self.compute_start_end_step()

    def slice(self, start: datetime = None, end: datetime = None) -> "MarketHistory":
        """ Discard all records outside of the slice window defined by start and end. """

        assert (
            start or end
        ), "To construct a slice, provide one or both of [start, end]."
        if start and end:
            assert start < end
        new = MarketHistory(self.market)

        for k, v in self._data.items():
            if start and k < start:
                continue
            if end and k >= end:
                continue
            new.add_record(k, *v)

        new.compute_start_end_step()
        return new

    @property
    def start(self) -> datetime:
        if self._dirty_bit:
            self.compute_start_end_step()
        return self._start

    @property
    def end(self) -> datetime:
        if self._dirty_bit:
            self.compute_start_end_step()
        return self._end

    def __iter__(self) -> Iterator[Tuple[float, float, float]]:
        if self._dirty_bit:
            self.compute_start_end_step()
        return iter(self._data.values())

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        if self._dirty_bit:
            self.compute_start_end_step()

        if item in self._data:
            return self._data[item]
        else:
            if item < self.start:
                raise KeyError(f"Dataset starts at {self.start}, prices at {item} are not known.")
            idx = bisect.bisect(self._keys, item) - 1
            key = self._keys[idx]
            return self._data[key]

    def plot(self):

        prices = [(low + high) / 2 for low, high, delta in self]

        from bokeh.plotting import figure, show

        p = figure(
            title=f"{self.market.name} - {self.market.code}", x_axis_label="x", y_axis_label="y", width=1200
        )

        p.line(list(range(len(prices))), prices, legend_label="price", line_width=1, color="blue")
        show(p)
