from env.abc.position import Position
from env.abc.market_data import MarketData

INTEREST_LONG = 1 / 1500
INTEREST_SHORT = 1 / 4000


class SimPosition(Position):
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""

    def __init__(self, amount, market_data: MarketData, limit=None, stop=None):

        ask, bid = market_data.ask, market_data.bid

        if amount > 0:
            price = ask
            self._cost = amount * price
        else:
            price = bid
            self._win = abs(amount) * price

        super().__init__(amount, price, market_data, limit, stop)

    def profit(self):

        if self.amount > 0:
            cost = self._cost
            win = self.amount * self.market_data.bid
        else:
            win = self._win
            cost = abs(self.amount) * self.market_data.ask
        return win - cost

    def daily_cost(self):
        ask, bid = self.market_data.ask, self.market_data.bid
        value = abs(self.amount) * (ask + bid) / 2
        if self.amount > 0:
            return value * INTEREST_LONG
        else:
            return value * INTEREST_SHORT
