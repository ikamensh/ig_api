from typing import Dict

from src.robotrader.robotrader import RoboTrader

from src.robotrader.features.features import ExpAvg, price, Momentum
from src.robotrader.features.derived_features import expavg_stddev
from trading_api.exceptions import (
    InsufficientFundsException,
)


class SmartShort(RoboTrader):
    def __init__(self, sess, market_id, steps_per_day):
        super().__init__(sess, market_id, steps_per_day)

        self.day_dev = expavg_stddev(window=steps_per_day * 5)
        self.price_avg_30 = ExpAvg(beta=self._beta_days(30), fn=price)

        self.features = {
            "day_dev": self.day_dev,
            "price_avg_30": self.price_avg_30,
        }

    def debug_info(self) -> Dict[str, float]:
        result = {}
        # result["free"] = self.free
        # result["delta_30"] = self.delta_30
        # result["delta_100"] = self.delta_100
        result["delta"] = self.delta
        result["delta_thres_high"] = 0.6
        # result["delta_thres_low"] = -0.8
        # result["true_price"] = self.true_value

        return result

    @property
    def true_value(self):
        return self.price_avg_30.value

    @property
    def delta(self):
        """ Deviation from true value """
        return (price(self.market_data()) - self.true_value) / (
            self.price_avg_30.value / 20 + self.day_dev.value
        )

    def decide_actions(self):
        if self._free_money() < 0:
            return

        if self.delta > 0.7:
            try:
                amt = -int(self.max_short_amount() * 0.1)
                if amt:
                    lim_factor = -0.3
                    limit = self.market_data().bid * (1 + lim_factor)
                    # stop = (self.platform.market_ask + self.platform.market_bid) / 2 * (1 - 5 * lim_factor)
                    self.open(amt, limit=limit)
            except (InsufficientFundsException):
                pass
