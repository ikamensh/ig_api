from env.exceptions import InvalidBoundingPriceException, InsufficientFundsException
from src.robotrader.robotrader import RoboTrader

from src.robotrader.features.features import ExpAvg, Momentum, price
from src.robotrader.features.derived_features import expavg_stddev


class MomentumTrader(RoboTrader):
    def __init__(self, price_data, balance, steps_per_day, log):
        super().__init__(price_data, balance, steps_per_day, log)

        def beta_days( days ):
            return 1 - 0.6 / days

        self.day_dev = expavg_stddev(window=steps_per_day, smoothing=beta_days(30))
        self.week_dev = expavg_stddev(window=steps_per_day * 5, smoothing=beta_days(60))
        self.price_momentum = ExpAvg(beta=beta_days(15), fn=Momentum(price))
        self.price_avg = ExpAvg(beta=beta_days(15), fn=price)
        self.instant_momentum = ExpAvg(beta=0.75, fn=Momentum(price))

        self.features = {
            "day_dev": self.day_dev,
            "week_dev": self.week_dev,
            "price_momentum" : self.price_momentum,
            "instant_momentum" : self.instant_momentum,
            "price_avg" : self.price_avg
        }

    def decide_actions(self):

        free = ( self.account.balance - self.account.risk() * 2 ) / self.account.balance

        if free < 0.3:
            return

        future_price = self.price_avg.value + self.price_momentum.value * 5
        delta = price(self.price_data) - future_price
        self.history['delta'].append(delta)
        self.history['neg_day_dev'].append(-self.day_dev.value)
        self.history['neg_week_dev'].append(-self.week_dev.value)

        if abs(delta) > self.day_dev.value * 1.3:
            if delta < 0:
                amount = 10 * abs(delta) * free
                try:
                    self.account.open(
                        amount,
                        limit=max(price(self.price_data), future_price) + self.day_dev.value ,
                        stop=min(price(self.price_data), future_price) - self.day_dev.value
                    )
                except (InsufficientFundsException, InvalidBoundingPriceException):
                    pass

            else:
                amount = -10 * abs(delta) * free
                try:
                    self.account.open(
                        amount,
                        limit =min(price(self.price_data), future_price) - self.day_dev.value,
                        stop =max(price(self.price_data), future_price) + self.day_dev.value
                    )
                except (InsufficientFundsException, InvalidBoundingPriceException):
                    pass

