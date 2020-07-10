from src.robotrader.account import InsufficientFundsException
from src.robotrader.features.features import price
from src.robotrader.robotrader import RoboTrader


class MovingAvgTrader(RoboTrader):
    def __init__(self, platform, balance, steps_per_day):
        super().__init__(platform, balance, steps_per_day)

    def decide_actions(self):
        if self.account.risk() > self.account.balance:
            return

        future_price = self.price_avg.value + self.price_momentum.value
        delta = price(self.platform) - future_price
        self.history['delta'].append(delta)
        self.history['neg_day_dev'].append(-self.day_dev.value)
        self.history['neg_week_dev'].append(-self.week_dev.value)

        if abs(delta) > self.day_dev.value:
            if delta < 0:
                amount = 5
                try:
                    self.account.open(
                        amount,
                        limit=self.price_avg.value
                        + 0.08
                        + self.day_dev.value
                        + self.price_momentum.value,
                    )
                except InsufficientFundsException:
                    pass

            # else:
            #     amount = -5
            #     try:
            #         self.account.open(
            #             amount,
            #             limit=price(self.platform)
            #             - 0.8
            #             - self.day_dev.value
            #             + self.price_momentum.value,
            #         )
            #     except InsufficientFundsException:
            #         pass

