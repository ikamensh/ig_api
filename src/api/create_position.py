import requests

from api.login import headers
from const import demo_url
from env.position import Position
from api.latest_prices import get_price_data

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
    "currencyCode": "EUR"
}


def open_position(market, amount) -> str:
    body["epic"] = market
    body["size"] = abs(amount)
    headers["Version"] = "2"
    if amount < 0:
        body["direction"] = "SELL"
    else:
        body["direction"] = "BUY"

    r = requests.post(url=otc_url, headers=headers, json=body)
    assert r.status_code == 200
    del headers["Version"]

    return r.json()["dealReference"]


trade_confirm_url = demo_url + "confirms/"


def deal_confirm(deal_reference) -> Position:
    r = requests.get(url=f"{trade_confirm_url}/{deal_reference}", headers=headers)
    assert r.status_code == 200

    reply = r.json()
    status, reason = reply["dealStatus"], reply["reason"]
    print(status, reason)

    if status != "ACCEPTED":
        raise Exception(f"Failed to open position, reason: {reason}.")

    deal_id = reply["dealId"]
    price = float(reply["level"])

    amount = float(reply["size"])
    if reply["direction"] == "SELL":
        amount *= -1

    market = reply["epic"]

    return Position(amount=amount, price_data=get_price_data(market), price=price, deal_id=deal_id)


if __name__ == "__main__":
    import markets

    ref = open_position(markets.VIX, 20)
    pos = deal_confirm(ref)
    print(pos.deal_id)
