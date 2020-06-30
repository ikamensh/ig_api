from src.robotrader.account import InsufficientFundsException
from src.robotrader.features.features import price
from src.robotrader.robotrader import RoboTrader


class MovingAvgTrader(RoboTrader):
    def __init__(self, platform):
        super().__init__(platform)

    def decide_actions(self):
        future_price = self.price_avg.value + self.price_momentum.value * 10
        delta = price(self.platform) - future_price
        self.history['delta'].append(delta)

        # if abs(delta) > self.day_dev.value:
        #     if delta < 0:
        #         amount = delta * delta * 20
        #         try:
        #             self.account.open(
        #                 amount,
        #                 limit=self.price_avg.value
        #                 + 0.08
        #                 + self.day_dev.value
        #                 + self.price_momentum.value,
        #             )
        #         except InsufficientFundsException:
        #             pass

            # else:
            #     amount = delta * delta * -40
            #
            #     try:
            #         self.account.open(
            #             amount,
            #             limit=price(self.platform)
            #             - 0.16
            #             - self.day_variance.value
            #             + self.price_momentum.value,
            #         )
            #     except InsufficientFundsException:
            #         pass

