import requests

from const import demo_url
import markets
from src.api.login import headers

markets_url = demo_url + "prices/"

def bid_price(market):
    r = requests.get(url=markets_url + market, headers=headers)
    bid_price = r.json()["snapshot"]["bid"]
    return bid_price

print(bid_price(markets.VIX))