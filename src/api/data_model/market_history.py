import os
import csv

from api.ig_session import IgSession
from config import data_folder
import markets
import datetime


class MarketHistory:
    """ Stores data in .csv files.

    Assumes following row format: date, data\n"""

    def __init__(self, market: markets.MarketId, resolution):
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
                        d = datetime.datetime.fromisoformat(timestamp)
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



if __name__ == "__main__":
    from api.write_history import resolutions
    mh = MarketHistory(markets.vix, resolution=resolutions.HOUR_2)
    mh.to_csv()

