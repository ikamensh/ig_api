from random import randint, random

from robotrader.traders.potential_trader import PotentialTrader

from src.robotrader.features.derived_features import expavg_stddev
from src.robotrader.features.features import ExpAvg, Momentum, price

import math


def sigmoid(gamma):
  if gamma < 0:
    return 1 - 1/(1 + math.exp(gamma))
  else:
    return 1/(1 + math.exp(-gamma))


def hyperb_tan(x):
    return 2 * sigmoid(x) - 1


class EvoPotTrader(PotentialTrader):

    def risk_factor(self) -> float:
        return sigmoid(
            (self.mom_risk_s * self.momentum_short.value +
             self.mom_risk * self.momentum.value) /
            (self.dev_risk * self.dev.value + self.dev_s_risk * self.dev_short.value)
        )

    def potential(self) -> float:
        return hyperb_tan(
            (self.price_avg.value - price(self.market_data()) +
             self.mom_pot_s * self.momentum_short.value +
             self.mom_pot * self.momentum.value) / (
                        self.dev_pot * self.dev.value + self.dev_s_pot * self.dev_short.value)
        )

    @staticmethod
    def random_params():
        return [
            randint(1, 50), randint(5, 100), random() - 0.5, random() - 0.5,
            randint(10, 100), randint(10, 300), random() - 0.5, random() - 0.5,
            randint(1, 50), randint(30, 300),
            randint(1, 50), 10 * (random() - 0.5), 10 * (random() - 0.5),
            randint(10, 100), 10 * (random() - 0.5), 10 * (random() - 0.5),
            random(), random()
        ]

    def __init__(self, account, market_code, steps_per_day, *, params=None):
        super().__init__(account, market_code, steps_per_day)

        (
            window1, b_dev_s, self.dev_s_pot, self.dev_s_risk,
            window2, b_dev, self.dev_pot, self.dev_risk,
            b_avg_s, b_avg,
            b_mom_s, self.mom_pot_s, self.mom_risk_s,
            b_mom, self.mom_pot, self.mom_risk,
            self.short_limit, self.long_limit
        ) = params or self.random_params()


        self.dev_short = expavg_stddev(window=int(self.steps_per_day * window1))
        self.dev = expavg_stddev(window=int(self.steps_per_day * window2))

        self.price_avg_short = ExpAvg(beta=self._beta_days(b_avg_s), fn=price)
        self.price_avg = ExpAvg(beta=self._beta_days(b_avg), fn=price)

        self.momentum_short = ExpAvg(beta=self._beta_days(b_mom_s), fn=Momentum(price, steps_per_day))
        self.momentum = ExpAvg(beta=self._beta_days(b_mom), fn=Momentum(price, steps_per_day))

        self.features = {
            "dev_short": self.dev_short,
            "dev": self.dev,
            "price_avg_short": self.price_avg_short,
            "price_avg": self.price_avg,
            "momentum_short": self.momentum_short,
            "momentum": self.momentum,
        }
