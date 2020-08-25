import random

from trading_api.exceptions import InvalidBoundingPriceException, InsufficientFundsException
from src.robotrader.robotrader import RoboTrader


class MaxShortTrader(RoboTrader):
    def decide_actions(self):
        if self._free_money() < 0:
            return

        if random.random() < 0.03:
            try:
                amt = - int(self.max_short_amount() * 0.1)
                if amt:
                    lim_factor = -0.2
                    limit = self.market_data().bid * (1 + lim_factor)
                    # stop = (self.platform.market_ask + self.platform.market_bid) / 2 * (1 - 5 * lim_factor)
                    self.open(amt, limit=limit)
            except (InsufficientFundsException, InvalidBoundingPriceException):
                pass
