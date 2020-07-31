from api.data_model.market_data import MarketData
from api.exceptions import InvalidBoundingPriceException

INTEREST_LONG = 1 / 1500
INTEREST_SHORT = 1 / 4000



class Position:
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""

    sim_counter = 1

    def __init__(self, amount: int, market_data: MarketData, price, deal_id = None, limit=None, stop=None):
        if deal_id is None:
            deal_id = f"Sim Deal {Position.sim_counter}"
            Position.sim_counter += 1

        self.deal_id = deal_id

        if amount > 0:
            self._cost = amount * price
        else:
            self._win = abs(amount) * price

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

    def __repr__(self):
        result = f"Position {self.deal_id} in {self.market_data.market_id} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False

        if self.deal_id == other.deal_id:
            assert self.amount == other.amount
            assert self.market_data == other.market_data
            return True

        return False

    def __hash__(self):
        return hash(self.deal_id)


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


    def margin(self):
        """Minimum balance to keep this position open. """
        ask, bid = self.market_data.ask, self.market_data.bid
        value = abs(self.amount) * (bid + ask) / 2
        return self.market_data.margin_req * value
