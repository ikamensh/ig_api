from env.exceptions import InvalidBoundingPriceException
from env.abc.market_data import MarketData

from abc import ABC

class Position(ABC):
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""
    def __init__(self, amount, price, market_data: MarketData, limit=None, stop=None):
        self.amount = amount
        self.market_data = market_data
        self.price = price

        try:
            if amount > 0:
                if limit:
                    assert limit > self.price
                if stop:
                    assert stop < self.price
            else:
                if limit:
                    assert limit < self.price
                if stop:
                    assert stop > self.price
        except AssertionError as e:
            raise InvalidBoundingPriceException from e

        self.limit = limit
        self.stop = stop


    def risk(self):
        """Amount of worst-case loss due to this position. """
        if self.amount > 0:
            return self.amount * (self.price - self.market_data.lowest)
        else:
            return abs(self.amount) * (self.market_data.highest - self.price)

    def margin(self):
        """Minimum balance to keep this position open. """
        ask, bid = self.market_data.ask, self.market_data.bid
        value = abs(self.amount) * (bid + ask) / 2
        return self.market_data.margin_req * value


    def __repr__(self):
        result = f"{self.__class__.__name__} in {self.market_data.market_id} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit:.2f}"
        if self.stop:
            result += f" stop: {self.stop:.2f}"
        return result

