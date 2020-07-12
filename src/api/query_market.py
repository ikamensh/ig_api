import requests

from const import demo_url
import markets
from src.api.login import headers

markets_url = demo_url + "markets/"


class Snapshot:
    def __init__(self, json_elem, market):
        self.status = json_elem["marketStatus"]
        self.bid = json_elem["bid"]
        self.offer = json_elem["offer"]
        self.update_time = json_elem["updateTime"]

        self.market = market

    def __repr__(self):
        return f"market {self.market} is in status {self.status}, prices: {self.bid} | {self.offer} (updated at {self.update_time})"

def get_snapshot(market) -> Snapshot:
    r = requests.get(url=markets_url + market, headers=headers)
    assert r.status_code == 200
    return Snapshot(r.json()["snapshot"], market)


vix_snapshot = get_snapshot(markets.VIX)
print(vix_snapshot)
