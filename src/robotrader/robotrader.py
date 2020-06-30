import typing
import collections

from src.robotrader.account import Account
from src.robotrader.features.features import Feature, WindowVariance, ExpAvg, Momentum, price
from src.robotrader.features.derived_features import expavg_stddev

STEPS_PER_DAY = 4

class RoboTrader:
    def __init__(self, platform, balance=5000):
        self.account = Account(platform, balance)
        self.platform = platform

        beta_15_days = 1 - 0.04 / STEPS_PER_DAY
        beta_30_days = 1 - 0.02 / STEPS_PER_DAY
        beta_60_days = 1 - 0.01 / STEPS_PER_DAY
        self.day_dev = expavg_stddev(window=STEPS_PER_DAY, smoothing=beta_30_days)
        self.week_dev = expavg_stddev(window=STEPS_PER_DAY * 5, smoothing=beta_60_days)
        self.price_momentum = ExpAvg(beta=beta_15_days, fn=Momentum(price))
        self.price_avg = ExpAvg(beta=beta_15_days, fn=price)
        self.instant_momentum = ExpAvg(beta=0.51, fn=Momentum(price))

        self.features: typing.Dict[str, Feature] = {
            "day_dev": self.day_dev,
            "week_dev": self.week_dev,
            "price_momentum" : self.price_momentum,
            "instant_momentum" : self.instant_momentum,
            "price_avg" : self.price_avg
        }

        self.history = collections.defaultdict(list)

    def step(self):
        self.account.step()

        for k, f in self.features.items():
            f.update(self.platform)
            self.history[k].append(f.value)

        self.decide_actions()
        self.history['position'].append(self.account.asset())
        self.history['price'].append( price(self.platform) )
        self.history['price_high'].append( self.platform.high_bid )
        self.history['price_low'].append( self.platform.low_ask)

    def decide_actions(self):
        raise NotImplementedError
