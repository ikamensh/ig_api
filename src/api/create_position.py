import requests

from api.login import headers
from const import demo_url

acc_url = demo_url + "positions/otc/"


body ={
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

    r = requests.post(url=acc_url, headers=headers, json=body)
    assert r.status_code == 200
    del headers["Version"]

    return r.json()["dealReference"]


if __name__ == "__main__":
    import markets
    print(open_position(markets.VIX, 20))

