import requests

from api.login import headers
from const import demo_url
from env.real.position import RealPosition


def close_position(pos: RealPosition) -> None:
    otc_url = demo_url + "positions/otc"

    body = {
        "dealId": pos.deal_id,
        "epic": None,
        "expiry": None,
        "level": None,
        "orderType": "MARKET",
        "timeInForce": None,
        "quoteId": None,
        "size": str(abs(int(pos.amount))),
    }

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
    from api.create_position import _open_position, _deal_confirm
    from api.get_positions import get_positions

    print(len(get_positions()))

    ref = _open_position(markets.VIX, 20)
    pos = _deal_confirm(ref)
    print(pos.deal_id)
    print(len(get_positions()))

    close_position(pos)
    print(len(get_positions()))
