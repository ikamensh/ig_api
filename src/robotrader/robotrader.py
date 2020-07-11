import collections
import typing

from src.robotrader.features.features import price
from env.account import Account
from env.price_data import PriceData

if typing.TYPE_CHECKING:
    from robotrader.features.features import Feature


class RoboTrader:
    def __init__(self, price_data: PriceData, balance, steps_per_day: int, log: typing.List):
        self.account = Account(price_data, balance, steps_per_day, log)
        self.platform = price_data
        self.history = collections.defaultdict(list)
        self.features: typing.Dict[str, Feature] = {}


    def step(self):
        self.account.step()

        for k, f in self.features.items():
            f.update(self.platform)
            self.history[k].append(f.value)

        self.decide_actions()
        self.history['position'].append(self.account.asset())
        self.history['price'].append( price(self.platform) )
        self.history['balance'].append(self.account.balance)

    def decide_actions(self):
        raise NotImplementedError
