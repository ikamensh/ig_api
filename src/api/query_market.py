import requests

from const import demo_url
import markets
from env.real.market_data import RealMarket
from src.api.login import headers

markets_url = demo_url + "markets/"


class Snapshot:
    def __init__(self, json_elem):
        self.status = json_elem["marketStatus"]
        self.net_change = json_elem["netChange"]
        self.percentage_change = json_elem["percentageChange"]
        self.update_time = json_elem["updateTime"]
        self.delay_time = json_elem["delayTime"]
        self.bid = json_elem["bid"]
        self.offer = json_elem["offer"]
        self.low = json_elem["low"]
        self.high = json_elem["high"]

        if self.offer is None or self.bid is None:  # TODO raise exception instead
            self.delta = None
        else:
            self.delta = self.offer - self.bid


def get_market_data(market) -> RealMarket:
    headers["Version"] = "3"
    r = requests.get(url=markets_url + market, headers=headers)
    del headers["Version"]
    assert r.status_code == 200
    reply = r.json()
    snap = Snapshot(reply["snapshot"])
    instrument_el = reply["instrument"]
    dealing_rules = reply["dealingRules"]

    market_id = instrument_el["epic"]
    assert instrument_el["marginFactorUnit"] == "PERCENTAGE"
    margin_req = float(instrument_el["marginFactor"]) / 100

    return RealMarket(
        market_id=market_id, bid=snap.bid, ask=snap.offer, margin_req=margin_req
    )


if __name__ == "__main__":
    vix_market_data = get_market_data(markets.VIX)
    print(vix_market_data)
