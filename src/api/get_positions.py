import requests
from typing import List
from unittest.mock import Mock

from const import demo_url
import markets
from env.price_data import PriceData
from src.api.login import headers

from env.position import Position
from bot.latest_prices import latest_prices


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

        market_id = market["epic"]
        market_name = market["instrumentName"]

        if market_id in latest_prices:
            price_data = latest_prices[market_id]
        else:
            delta = market["offer"] - market["bid"]
            price_data = PriceData(delta, market_id=market_id)
            latest_prices[market_id] = price_data

        pos = Position(amount, price_data)
        pos.price = price
        result.append(pos)

    return result


if __name__ == "__main__":
    print(get_positions())