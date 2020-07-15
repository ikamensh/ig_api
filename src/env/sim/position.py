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
        else:
            price = bid

        super().__init__(amount, price, market_data, limit, stop)

    def profit(self, *, mode="market"):
        if mode == "market":
            ask, bid = self.market_data.ask, self.market_data.bid
        elif mode == "high":
            ask, bid = self.market_data.high_ask, self.market_data.high_bid
        elif mode == "low":
            ask, bid = self.market_data.low_ask, self.market_data.low_bid
        else:
            raise Exception(f"invalid mode: {mode}")

        if self.amount > 0:
            cost = self.amount * self.price
            win = self.amount * bid
        else:
            win = abs(self.amount) * self.price
            cost = abs(self.amount) * ask
        return win - cost

    def daily_cost(self):
        ask, bid = self.market_data.ask, self.market_data.bid
        value = abs(self.amount) * (ask + bid) / 2
        if self.amount > 0:
            return value * INTEREST_LONG
        else:
            return value * INTEREST_SHORT
