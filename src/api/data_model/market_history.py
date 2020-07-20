import copy
import os
import csv
from collections import Counter

from api.ig_session import IgSession
from config import data_folder
import markets
import datetime

from datasets.historical import iter_my_format
from datasets.price_dataset import PriceDataset, SyntheticDataset


class Resolutions:
    MINUTE_30 = "MINUTE_30"
    HOUR_2 = "HOUR_2"


def _default_date_parser(timestamp: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(timestamp)


class MarketHistory:
    """ Stores data in .csv files.

    Assumes following row format: date, data\n"""

    def __init__(self, market: markets.MarketId, resolution: str, date_parser=_default_date_parser):
        self.csv_path = os.path.join(data_folder, f"{market.name}.csv")
        self.market = market
        self.resolution = resolution
        self.data = {}
        if os.path.exists(self.csv_path):
            with open(self.csv_path) as f:
                r = csv.reader(f)
                for t in r:
                    timestamp, data = t[0], t[1:]
                    try:
                        d = date_parser(timestamp)
                    except Exception as e:
                        print(e)
                    else:
                        self.data[d] = data

        self.start = min(self.data.keys()) if self.data else None
        self.end = max(self.data.keys()) if self.data else None

    def to_csv(self):
        with open(self.csv_path, "w") as f:
            writer = csv.writer(f, delimiter=",")
            for k, v in sorted(self.data.items()):
                writer.writerow((k, *v))

    def update(self, sess: IgSession):
        if datetime.datetime.now() - self.end > datetime.timedelta(minutes=15):
            for t, *d in sess.price_history(
                    self.market.code, self.resolution, start=self.end, end=datetime.datetime.now()
            ):
                self.data[datetime.datetime.fromisoformat(t)] = d

            self.start = min(self.data.keys())
            self.end = max(self.data.keys())
            self.to_csv()

    def slice(self, start: datetime.datetime = None, end: datetime.datetime = None) -> None:
        assert start or end
        to_delete = []
        for k, v in self.data:
            if start and k < start:
                to_delete.append(k)
            if end and k > end:
                to_delete.append(k)

        for k in to_delete:
            del self.data[k]

    def to_dataset(self, decoder=iter_my_format) -> SyntheticDataset:

        days = [datetime.datetime(year=k.year, month=k.month, day=k.day) for k in self.data]
        ctr = Counter(days)

        steps_per_day = ctr[ctr.most_common()]
        result = SyntheticDataset(steps_per_day=steps_per_day)

        items = [(k, v) for k, v in sorted(self.data.items())]
        values = [v for _, v in items]

        for low, high, delta in decoder(values):
            result.add_record(low, high, delta)

        return result


if __name__ == "__main__":
    mh_ig = MarketHistory(markets.vix, resolution=Resolutions.HOUR_2)

    mh_official = MarketHistory(markets.vix_official, resolution=None)

    slice = [(k, v) for k, v in mh_official.data.items() if mh_ig.start <= k <= mh_ig.end]

    # mh.to_csv()
