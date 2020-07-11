import random

from env.exceptions import InsufficientFundsException, InvalidBoundingPriceException
from src.robotrader.robotrader import RoboTrader


class RandomTrader(RoboTrader):
    def decide_actions(self):
        if self.account.risk() > self.account.balance:
            return

        if random.random() < 0.1:
            try:
                amt = random.choice([-20, 20])
                lim_factor = -0.1 if amt < 0 else 0.1
                # limit = (self.platform.market_ask + self.platform.market_bid) / 2 * (1 + lim_factor)
                # stop = (self.platform.market_ask + self.platform.market_bid) / 2 * (1 - 5 * lim_factor)
                # self.account.open(amt, limit=limit, stop=stop)
                self.account.open(amt)
            except (InsufficientFundsException, InvalidBoundingPriceException):
                pass

        if self.account.positions and random.random() < 0.15:
        # if self.account.positions and random.random() < 0.05:
            pos = random.choice(self.account.positions)
            self.account.close(pos)