import requests
from typing import List

from const import demo_url
from src.api.login import headers

from env.sim.position import Position
from api.latest_prices import get_price_data

positions_url = demo_url + "positions/"


def get_positions() -> List[Position]:
    headers["Version"] = "2"
    r = requests.get(url=positions_url, headers=headers)
    assert r.status_code == 200
    result = []
    for pos_elem in r.json()["positions"]:
        pos = pos_elem["position"]
        market = pos_elem["market"]

        amount = pos["size"]
        if pos["direction"] == "SELL":
            amount *= -1

        price = float(pos["level"])
        deal_id = pos["dealId"]

        market_id = market["epic"]
        market_name = market["instrumentName"]

        pos = Position(amount, get_price_data(market_id), deal_id=deal_id)
        pos.price = price
        result.append(pos)

    del headers["Version"]
    return result


if __name__ == "__main__":
    print(get_positions())
