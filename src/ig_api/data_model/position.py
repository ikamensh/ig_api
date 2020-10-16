from ig_api.data_model.market_data import MarketData
from ig_api.exceptions import InvalidBoundingPriceException


def _verify_limit_stop(amount, limit, price, stop):
    try:
        if amount > 0:
            _limit_stop_long(limit, price, stop)
        else:
            _limit_stop_short(limit, price, stop)
    except AssertionError as e:
        raise InvalidBoundingPriceException from e


def _limit_stop_long(limit, price, stop):
    if limit:
        assert limit > price
    if stop:
        assert stop < price


def _limit_stop_short(limit, price, stop):
    if limit:
        assert limit < price
    if stop:
        assert stop > price


class Position:
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""

    def __init__(
            self,
            amount: int,
            market_data: MarketData,
            price,
            deal_id,
            limit=None,
            stop=None,
    ):
        _verify_limit_stop(amount, limit, price, stop)
        self.deal_id = deal_id

        if amount > 0:
            self._cost = amount * price
        else:
            self._win = abs(amount) * price

        self.amount = amount
        self.market_data = market_data  # go to market code?
        self.price = price
        self.limit = limit
        self.stop = stop


    def __repr__(self):
        result = f"Position {self.deal_id} in {self.market_data.market_code} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False

        if self.deal_id == other.deal_id:
            assert self.amount == other.amount, "Inconsistency: deals with same id have to be equal"
            assert self.market_data == other.market_data, "Inconsistency: deals with same id have to be equal"
            return True

        return False

    def __hash__(self):
        return hash(self.deal_id)

    @property
    def market_code(self):
        return self.market_data.market_code

    def profit(self):
        """Calculate profit of closing the position at current prices. """
        if self.amount > 0:
            cost = self._cost
            win = self.amount * self.market_data.bid
        else:
            win = self._win
            cost = abs(self.amount) * self.market_data.ask
        return win - cost

    def margin(self):
        """Minimum balance to keep this position open. """
        ask, bid = self.market_data.ask, self.market_data.bid
        value = abs(self.amount) * (bid + ask) / 2
        return self.market_data.margin_req * value
