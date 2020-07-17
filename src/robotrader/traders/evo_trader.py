import random

from src.robotrader.robotrader import RoboTrader

from src.robotrader.features.features import ExpAvg, price
from src.robotrader.features.derived_features import expavg_stddev


class EvoTrader(RoboTrader):

    @staticmethod
    def random_params():
        return [
            random.randint(10, 400),
            random.randint(10, 400),

            random.random(),
            random.random(),
            random.random(),

            random.random(),
            random.random(),
            random.random(),

            random.random(),
            random.random(),

            random.randint(10, 400),
            random.randint(1, 30),
            random.random(),
        ]


    def __init__(self, account, market_data, steps_per_day, *, params = None):
        super().__init__(account, market_data, steps_per_day)

        (
            beta1,
            beta2,

            self.risk_factor,
            self.long_limit,
            self.short_limit,

            self.f05,
            self.f1,
            self.f2,

            self.low_bound,
            self.high_bound,

            beta3,
            window,
            self.fd,
        ) = params or self.random_params()


        self.day_dev = expavg_stddev(window=int(self.steps_per_day * window), smoothing=self.beta_days(beta3))

        self.price_avg_30 = ExpAvg(beta=self.beta_days(beta1), fn=price)
        self.price_avg_100 = ExpAvg(beta=self.beta_days(beta2), fn=price)

        self.features = {
            "day_dev": self.day_dev,
            "price_avg_30": self.price_avg_30,
            "price_avg_100": self.price_avg_100,
        }

    def decide_actions(self):

        free = (
            self.account.balance - self.account.risk() - self.account.margin()
        ) / self.account.balance

        if free < 0.3:
            return

        delta_30 = (
            price(self.market_data) - self.price_avg_30.value
        ) / self.price_avg_30.value
        delta_100 = (
            price(self.market_data) - self.price_avg_100.value
        ) / self.price_avg_100.value

        if delta_30 * delta_100 < 0:
            return

        if delta_30 < 0:
            delta = max(delta_30, delta_100)
        else:
            delta = min(delta_30, delta_100)

        factor = (
            self.f05 * (abs(delta) ** (1 / 2))
            + self.f1 * delta
            + self.f2 * (abs(delta) ** 2)
        )

        delta *= (1 + ( - 0.5 + self.fd * self.day_dev.value))

        if delta < - self.low_bound:  # low price - close short, open long
            while (
                self.account.positions and (p := self.account.positions[-1]).amount < 0
            ):
                self.account.close(p)

            max_amt = self.max_long_amount()
            self.account.open(
                max(1, int(factor * max_amt)),
                market=self.market_data.market_id,
                limit=self.market_data.ask * (1 + self.long_limit),
            )

        elif delta > self.high_bound:  # high price - close long, open short positions
            while (
                self.account.positions and (p := self.account.positions[-1]).amount > 0
            ):
                self.account.close(p)

            max_amt = self.max_short_amount()
            self.account.open(
                -max(1, int(factor * max_amt)),
                market=self.market_data.market_id,
                limit=self.market_data.bid * (1 - self.short_limit),
            )

    def max_long_amount(self):

        free_money = self.account.balance - self.risk_factor * self.account.risk()
        risk_per_unit = self.market_data.ask - self.market_data.lowest

        return free_money / risk_per_unit

    def max_short_amount(self):
        free_money = self.account.balance - self.risk_factor * self.account.risk()
        risk_per_unit = self.market_data.highest - self.market_data.bid

        return free_money / risk_per_unit
