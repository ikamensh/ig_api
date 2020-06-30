import random

from src.robotrader.account import InsufficientFundsException
from src.robotrader.robotrader import RoboTrader


class RandomTrader(RoboTrader):
    def decide_actions(self):
        if random.random() < 0.1:
            try:
                amt = random.choice([-20, 20])
                lim_factor = -0.1 if amt < 0 else 0.1
                limit = (self.platform.market_ask + self.platform.market_bid) / 2 * (1 + lim_factor)
                stop = (self.platform.market_ask + self.platform.market_bid) / 2 * (1 - 5 * lim_factor)
                self.account.open(amt, limit=limit, stop=stop)
            except InsufficientFundsException:
                pass

        if self.account.positions and random.random() < 0.05:
            pos = random.choice(self.account.positions)
            self.account.close(pos)