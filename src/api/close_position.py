import requests

from api.login import headers
from const import demo_url
from env.position import Position

otc_url = demo_url + "positions/otc"


body = {
    "dealId": "DIAAAAD3V6WH2A2",
    "epic": None,
    "expiry": None,
    "direction": "SELL",
    "level": None,
    "orderType": "MARKET",
    "timeInForce": None,
    "quoteId": None
}


def close_position(pos: Position) -> None:
    body["size"] = str( abs(int(pos.amount)) )
    body["dealId"] = pos.deal_id

    if pos.amount < 0:
        body["direction"] = "BUY"
    else:
        body["direction"] = "SELL"

    headers["_method"] = "DELETE"
    r = requests.post(url=otc_url, headers=headers, json=body)
    del headers["_method"]

    assert r.status_code == 200, r.text


if __name__ == "__main__":
    import markets
    from api.create_position import open_position, deal_confirm
    from api.get_positions import get_positions

    print(len(get_positions()))

    ref = open_position(markets.VIX, 20)
    pos = deal_confirm(ref)
    print(pos.deal_id)
    print(len(get_positions()))

    close_position(pos)
    print(len(get_positions()))

