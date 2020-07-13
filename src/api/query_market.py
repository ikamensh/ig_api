import requests

from const import demo_url
import markets
from src.api.login import headers

markets_url = demo_url + "markets/"


class Snapshot:
    def __init__(self, json_elem, market_id):
        self.status = json_elem["marketStatus"]
        self.bid = json_elem["bid"]
        self.offer = json_elem["offer"]
        self.update_time = json_elem["updateTime"]
        if self.offer is None or self.bid is None:  # why does this happen? idk.
            self.delta = None
        else:
            self.delta = self.offer - self.bid

        self.low = json_elem["low"]
        self.high = json_elem["high"]

        self.market = market_id

    def __repr__(self):
        return f"market {self.market} is in status {self.status}, " \
               f"prices: {self.bid} | {self.offer} (updated at {self.update_time})"


def get_snapshot(market) -> Snapshot:
    r = requests.get(url=markets_url + market, headers=headers)
    assert r.status_code == 200
    return Snapshot(r.json()["snapshot"], market)


if __name__ == "__main__":
    vix_snapshot = get_snapshot(markets.VIX)
    print(vix_snapshot)
