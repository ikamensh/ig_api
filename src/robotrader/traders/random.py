import random

from trading_api.exceptions import InvalidBoundingPriceException, InsufficientFundsException
from src.robotrader.robotrader import RoboTrader


class RandomTrader(RoboTrader):
    def decide_actions(self):
        if self._risk() > self.available:
            return

        if random.random() < 0.1:
            try:
                amt = random.choice([-20, 20])
                lim_factor = -0.1 if amt < 0 else 0.1
                limit = (self.market_data().ask + self.market_data().bid) / 2 * (1 + lim_factor)
                stop = (self.market_data().ask + self.market_data().bid) / 2 * (1 - 5 * lim_factor)
                self.open(amt, limit=limit, stop=stop)
                # self.open(amt)
            except (InsufficientFundsException, InvalidBoundingPriceException):
                pass

        if self.sess.get_positions() and random.random() < 0.05:
        # if self.account.positions and random.random() < 0.05:
            pos = random.choice(self.sess.get_positions())
            self.close(pos)