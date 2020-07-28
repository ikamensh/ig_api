import os
import csv
from collections import Counter
from typing import Dict, Tuple, Iterator

from api.ig_session import IgSession
from config import data_folder
import markets
import datetime


class Resolutions:
    MINUTE_30 = "MINUTE_30"
    HOUR_2 = "HOUR_2"

    __all__ = [MINUTE_30, HOUR_2]


def parse_date(timestamp: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(timestamp)


class MarketHistory:
    """ Represents available historic data for a given market.

    Handles:
        1) iteration over the data
        2) saving and loading to .csv file
        3) slicing data based on datetime
    """

    def __init__(self, market: markets.MarketId):
        self.csv_path = os.path.join(data_folder, f"{market.name}.csv")
        self.market = market
        self._data: Dict[datetime, Tuple[float, float, float]] = {}
        self._start = None
        self._end = None
        self.steps_per_day = None
        self._dirty_bit = False

    def compute_start_end_step(self):
        """ Housekeeping - sort the data, find earliest and latest datetime, detect steps per day. """
        srtd = sorted(self._data.items())
        self._start = srtd[0][0] if self._data else None
        self._end = srtd[-1][0] if self._data else None
        self._data = {k:v for k, v in sorted(self._data.items())}

        days = [datetime.datetime(year=k.year, month=k.month, day=k.day) for k in self._data]
        ctr = Counter(days)
        self.steps_per_day = ctr[ctr.most_common()[0]]

        self._dirty_bit = False

    def add_record(self, *, date_time: datetime.datetime, low: float, high: float, delta: float):
        """ Add a single record. """

        self._dirty_bit = True
        self._data[date_time] = low, high, delta

    @staticmethod
    def from_csv(market: markets.MarketId):
        """ Create an MarketHistory based on the data saved in a .csv file.

        Symmetrical with `to_csv` method. """

        result = MarketHistory(market)

        if not os.path.exists(result.csv_path):
            raise FileNotFoundError

        with open(result.csv_path) as f:
            r = csv.reader(f)
            for t in r:
                timestamp, data = t[0], t[1:]
                low, high, delta = [float(x) for x in data]

                d = parse_date(timestamp)
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

    def update(self, sess: IgSession, resolution):
        """ Use session to update data to the latest available on the platform. """

        assert resolution in Resolutions.__all__, f"Unsupported resolution {resolution}."

        if datetime.datetime.now() - self.end > datetime.timedelta(minutes=15):
            for t, (low, high, delta) in sess.price_history(
                    self.market.code, resolution, start=self.end, end=datetime.datetime.now()
            ):
                self._data[datetime.datetime.fromisoformat(t)] = low, high, delta
            self.compute_start_end_step()

    def slice(self, start: datetime.datetime = None, end: datetime.datetime = None) -> "MarketHistory":
        """ Discard all records outside of the slice window defined by start and end. """

        assert start or end, "To construct a slice, provide one or both of [start, end]."
        new = MarketHistory(self.market)

        for k, v in self._data.items():
            if start and k < start:
                continue
            if end and k > end:
                continue
            new.add_record(k, *v)

        new.compute_start_end_step()
        return new

    @property
    def start(self):
        if self._dirty_bit:
            self.compute_start_end_step()
        return self._start

    @property
    def end(self):
        if self._dirty_bit:
            self.compute_start_end_step()
        return self._end

    def __iter__(self) -> Iterator[Tuple[float, float, float]]:
        if self._dirty_bit:
            self.compute_start_end_step()
        return iter(self._data.values())

    def __len__(self):
        return len(self._data)

    # def add_averaging(self) -> None:
    #
    #     items = [(k, v) for k, v in sorted(self.data.items())]
    #     values =
    #
    #     days_fast = 5
    #     beta_fast = 1 - 0.6 / days_fast
    #     avg_fast = sum((l + h) / 2 for _, l, h, _ in dataset.data[:100])
    #
    #     days_slow = 150
    #     beta_slow = 1 - 0.6 / days_slow
    #     avg_slow = sum((l + h) / 2 for _, l, h, _ in dataset.data[:500])
    #
    #     for date, low, high, delta in dataset.data:
    #         avg_fast = avg_fast * beta_fast + (low + high) / 2 * (1 - beta_fast)
    #
    #         avg_slow = avg_slow * beta_slow + (low + high) / 2 * (1 - beta_slow)
    #
    #         result.add_record(
    #             (2 * low + avg_fast + avg_slow) / 4,
    #             (2 * high + avg_fast + avg_slow) / 4,
    #             delta,
    #         )
    #
    #     return result


if __name__ == "__main__":
    mh_ig = MarketHistory(markets.vix)

    mh_official = MarketHistory(markets.vix_official)

    for a, b in mh_ig:
        pass
