from env.abc.position import Position
from env.abc.market_data import MarketData

class RealPosition(Position):
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""

    def __init__(self, amount: int, market_data: MarketData, price, deal_id, limit=None, stop=None):
        self.deal_id = deal_id
        super().__init__(amount, price, market_data, limit, stop)

    def __repr__(self):
        result = f"Real Position {self.deal_id} in {self.market_data.market_id} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

    def __eq__(self, other):
        if not isinstance(other, RealPosition):
            return False

        if self.deal_id == other.deal_id:
            assert self.amount == other.amount
            assert self.market_data == other.market_data
            return True

        return False

    def __hash__(self):
        return hash(self.deal_id)

