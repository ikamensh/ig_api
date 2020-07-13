import requests

from api.login import headers
from const import demo_url
from env.real.position import RealPosition
from env.sim.position import Position
from api.latest_prices import get_price_data


def _open_position(market, amount) -> str:
    otc_url = demo_url + "positions/otc/"

    body = {
        "expiry": "-",
        "orderType": "MARKET",
        "timeInForce": None,
        "level": None,
        "guaranteedStop": "false",
        "stopLevel": None,
        "stopDistance": None,
        "trailingStop": None,
        "trailingStopIncrement": None,
        "forceOpen": "false",
        "limitLevel": None,
        "limitDistance": None,
        "quoteId": None,
        "currencyCode": "EUR",
        "epic": market,
        "size": abs(amount),
    }

    headers["Version"] = "2"
    if amount < 0:
        body["direction"] = "SELL"
    else:
        body["direction"] = "BUY"

    r = requests.post(url=otc_url, headers=headers, json=body)
    assert r.status_code == 200
    del headers["Version"]

    return r.json()["dealReference"]




def _deal_confirm(deal_reference) -> RealPosition:
    trade_confirm_url = demo_url + "confirms/"

    r = requests.get(url=f"{trade_confirm_url}/{deal_reference}", headers=headers)
    assert r.status_code == 200

    reply = r.json()
    status, reason = reply["dealStatus"], reply["reason"]
    print(status, reason)

    if status != "ACCEPTED":
        raise Exception(f"Failed to open position, reason: {reason}.")

    deal_id = reply["dealId"]
    price = float(reply["level"])

    amount = int(reply["size"])
    if reply["direction"] == "SELL":
        amount *= -1

    market = reply["epic"]

    return RealPosition(
        amount=amount, price_data=get_price_data(market), price=price, deal_id=deal_id
    )

def open_position(amount: int, market: str) -> RealPosition:
    ref = _open_position(market, amount)
    return _deal_confirm(ref)

if __name__ == "__main__":
    import markets
    print(open_position(20, markets.VIX))
