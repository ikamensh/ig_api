from typing import Dict

from src.robotrader.robotrader import RoboTrader

from src.robotrader.features.features import ExpAvg, price, Momentum
from src.robotrader.features.derived_features import expavg_stddev


class ExpAvgTrader(RoboTrader):
    def __init__(self, sess, market_id, steps_per_day):
        super().__init__(sess, market_id, steps_per_day)

        self.day_dev = expavg_stddev(window=steps_per_day * 5)

        self.price_avg_30 = ExpAvg(beta=self._beta_days(30), fn=price)
        self.price_avg_5 = ExpAvg(beta=self._beta_days(5), fn=price)
        self.momentum_short = ExpAvg(beta=self._beta_days(2.5), fn=(ExpAvg(beta=self._beta_days(0.5), fn=Momentum(price, steps_per_day))))
        self.momentum_mid = ExpAvg(beta=self._beta_days(6), fn=(ExpAvg(beta=self._beta_days(0.5), fn=Momentum(price, steps_per_day))))
        self.momentum = ExpAvg(beta=self._beta_days(20), fn=Momentum(price, steps_per_day))

        self.features = {
            "day_dev": self.day_dev,
            # "week_dev": self.week_dev,
            "price_avg_30": self.price_avg_30,
            "price_avg_5": self.price_avg_5,
            "momentum_short": self.momentum_short,
            "momentum_mid" : self.momentum_mid,
            "momentum": self.momentum,
        }

    @property
    def free(self):
        return (self.available - self._risk()) / self.balance

    def debug_info(self) -> Dict[str, float]:
        result = {}
        # result["free"] = self.free
        # result["delta_30"] = self.delta_30
        # result["delta_100"] = self.delta_100
        result["delta"] = self.delta
        result["delta_thres_high"] = 1.2
        result["delta_thres_low"] = -0.8
        # result["delta_momentum"] = self.delta
        result["true_price"] = self.true_value

        return result

    @property
    def true_value(self):
        return self.price_avg_5.value \
               + 15 * self.momentum.value \
               + 25 * self.momentum_mid.value \
               - 2 * self.momentum_short.value

    @property
    def delta(self):
        """ Deviation from true value """
        return 2 * (
            price(self.market_data()) - self.true_value
        ) / ( self.price_avg_30.value / 20 + self.day_dev.value )


    def decide_actions(self):



        v = self.delta
        factor = abs(v) ** 2

        if v < -0.5:  # low price - close short, open long
            if self.momentum_mid.value < 0:
                return

            while self.positions and (p := self.positions[-1]).amount < 0:
                self.close(p)

            if v < -1.5:  # low price - close short, open long
                if self.free < 0.3:
                    return

                max_amt = self.max_long_amount()
                if max_amt < 0:
                    return

                self.open(
                    max(3, int(factor * max_amt)), limit=self.market_data().ask * 1.1,
                )

        elif v > 0.3:  # high price - close long, open short positions
            if self.momentum_mid.value > 0:
                return

            while self.positions and (p := self.positions[-1]).amount > 0:
                self.close(p)

            if v > 0.9:  # high price - close long, open short positions
                if self.free < 0.3:
                    return

                max_amt = self.max_short_amount()
                if max_amt < 0:
                    return
                self.open(
                    -max(3, int(factor * max_amt)), limit=self.market_data().bid * 0.8,
                )
