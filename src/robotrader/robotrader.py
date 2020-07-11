import collections
import typing

from env.exceptions import CantOpenPosition
from env.position import MIN_PRICE, HIGH_PRICE
from src.robotrader.features.features import price
from env.account import Account
from env.price_data import PriceData

if typing.TYPE_CHECKING:
    from robotrader.features.features import Feature


class RoboTrader:
    def __init__(self, price_data: PriceData, balance, steps_per_day: int, log: typing.List):
        self.account = Account(price_data, balance, steps_per_day, log)
        self.price_data = price_data
        self.history = collections.defaultdict(list)
        self.features: typing.Dict[str, Feature] = {}


    def step(self):
        self.account.step()

        for k, f in self.features.items():
            f.update(self.price_data)
            self.history[k].append(f.value)


        try:
            self.decide_actions()
        except CantOpenPosition:
            pass

        self.history['position'].append(self.account.asset())
        self.history['price'].append(price(self.price_data))
        self.history['balance'].append(self.account.balance)

    def decide_actions(self):
        raise NotImplementedError


    def max_long_amount(self):

        free_money = self.account.balance - self.account.risk()
        risk_per_unit = self.price_data.market_ask - MIN_PRICE

        return free_money / risk_per_unit


    def max_short_amount(self):
        free_money = self.account.balance - self.account.risk()
        risk_per_unit = HIGH_PRICE - self.price_data.market_bid

        return free_money / risk_per_unit