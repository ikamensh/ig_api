from src.robotrader.robotrader import RoboTrader

from src.robotrader.features.features import ExpAvg, price
from src.robotrader.features.derived_features import expavg_stddev


class ExpAvgTrader(RoboTrader):
    def __init__(self, account, market_data, steps_per_day):
        super().__init__(account, market_data)

        def beta_days(days):
            return 1 - 0.6 / days

        self.day_dev = expavg_stddev(window=steps_per_day, smoothing=beta_days(30))
        self.week_dev = expavg_stddev(window=steps_per_day * 5, smoothing=beta_days(60))

        self.price_avg_30 = ExpAvg(beta=beta_days(30), fn=price)
        self.price_avg_100 = ExpAvg(beta=beta_days(100), fn=price)

        self.features = {
            "day_dev": self.day_dev,
            "week_dev": self.week_dev,
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

        if delta < -0.15:  # low price - close short, open long
            while (
                self.account.positions and (p := self.account.positions[-1]).amount < 0
            ):
                self.account.close(p)

            max_amt = self.max_long_amount()
            factor = abs(delta) ** 2
            self.account.open(
                max(1, int(factor * max_amt)),
                market=self.market_data.market_id,
                limit=self.market_data.ask * 1.2,
            )

        elif delta > 0.3:  # high price - close long, open short positions
            while (
                self.account.positions and (p := self.account.positions[-1]).amount > 0
            ):
                self.account.close(p)

            max_amt = self.max_short_amount()
            factor = abs(delta) ** 2
            self.account.open(
                -max(1, int(factor * max_amt)),
                market=self.market_data.market_id,
                limit=self.market_data.bid * 0.8,
            )
