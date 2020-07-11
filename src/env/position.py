from env.exceptions import InvalidBoundingPriceException
from env.price_data import PriceData

MIN_PRICE = 10
HIGH_PRICE = 90

INTEREST_LONG = 1 / 1500
INTEREST_SHORT = 1 / 4000


class Position:
    """A position in Volatility"""
    id = 1
    MARGIN_REQ = 0.2

    def __init__(self, amount, price_data: PriceData, limit=None, stop=None):
        self.platform = price_data
        ask, bid = price_data.market_ask, price_data.market_bid
        self.amount = amount

        try:
            if amount > 0:
                self.price = ask
                if limit:
                    assert limit > self.price
                if stop:
                    assert stop < self.price
            else:
                self.price = bid
                if limit:
                    assert limit < self.price
                if stop:
                    assert stop > self.price
        except AssertionError as e:
            raise InvalidBoundingPriceException from e

        self.id = Position.id
        Position.id += 1

        self.limit = limit
        self.stop = stop

    def profit(self, *, mode="market"):
        if mode == "market":
            ask, bid = self.platform.market_ask, self.platform.market_bid
        elif mode == "high":
            ask, bid = self.platform.high_ask, self.platform.high_bid
        elif mode == "low":
            ask, bid = self.platform.low_ask, self.platform.low_bid
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
        if self.amount > 0:
            return self.amount * (self.price - MIN_PRICE)
        else:
            return abs(self.amount) * (HIGH_PRICE - self.price)

    def margin(self):
        ask, bid = self.platform.market_ask, self.platform.market_bid
        value = abs(self.amount) * (bid + ask) / 2
        return self.MARGIN_REQ * value

    def daily_cost(self):
        ask, bid = self.platform.market_ask, self.platform.market_bid
        value = abs(self.amount) * (ask + bid) / 2
        if self.amount > 0:
            return value * INTEREST_LONG
        else:
            return value * INTEREST_SHORT

    def __repr__(self):
        result = f"Position {self.id} | {self.amount:.2f} @ {self.price:.2f},"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result
