from env.exceptions import InvalidBoundingPriceException

from abc import ABC

class Position(ABC):
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""
    def __init__(self, amount, price, price_data=None, limit=None, stop=None):
        self.amount = amount
        self.price_data = price_data
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
            return self.amount * (self.price - self.price_data.lowest)
        else:
            return abs(self.amount) * (self.price_data.highest - self.price)

    def margin(self):
        """Minimum balance to keep this position open. """
        ask, bid = self.price_data.market_ask, self.price_data.market_bid
        value = abs(self.amount) * (bid + ask) / 2
        return self.price_data.margin_req * value


    def __repr__(self):
        result = f"Position in {self.price_data.market_id} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

