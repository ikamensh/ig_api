from env.exceptions import InvalidBoundingPriceException
from env.price_data import PriceData

INTEREST_LONG = 1 / 1500
INTEREST_SHORT = 1 / 4000
MARGIN_REQ = 0.2


class Position:
    """A position in Volatility"""

    # TODO handle different markets - risk, etc.
    def __init__(self, amount, price_data: PriceData, limit=None, stop=None, price = None):
        self.amount = amount
        self.price_data = price_data


        if price:
            self.price = price
        else:
            ask, bid = price_data.market_ask, price_data.market_bid

            if amount > 0:
                self.price = ask
            else:
                self.price = bid

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

    def profit(self, *, mode="market"):
        if mode == "market":
            ask, bid = self.price_data.market_ask, self.price_data.market_bid
        elif mode == "high":
            ask, bid = self.price_data.high_ask, self.price_data.high_bid
        elif mode == "low":
            ask, bid = self.price_data.low_ask, self.price_data.low_bid
        else:
            raise Exception(f"invalid mode: {mode}")

        if self.amount > 0:
            cost = self.amount * self.price
            win = self.amount * bid
        else:
            win = abs(self.amount) * self.price
            cost = abs(self.amount) * ask
        return win - cost

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
        return MARGIN_REQ * value

    def daily_cost(self):
        ask, bid = self.price_data.market_ask, self.price_data.market_bid
        value = abs(self.amount) * (ask + bid) / 2
        if self.amount > 0:
            return value * INTEREST_LONG
        else:
            return value * INTEREST_SHORT

    def __repr__(self):
        result = f"Position in {self.price_data.market_id} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

