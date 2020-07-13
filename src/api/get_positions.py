import requests
from typing import List

from const import demo_url
import markets
from src.api.login import headers

from env.position import Position


positions_url = demo_url + "positions/"



def get_positions() -> List[Position]:
    r = requests.get(url=positions_url, headers=headers)
    assert r.status_code == 200
    result = []
    for pos_elem in r.json()["positions"]:
        pos = pos_elem["position"]
        market = pos_elem["market"]

        amount = pos["size"]
        if pos["direction"] == "SELL":
            amount *= -1

        market_id = market["epic"]
        market_name = market["instrumentName"]

        result.append(Position(amount, None, market=market_id))

    return result


if __name__ == "__main__":
    print(get_positions())