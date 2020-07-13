from env.abc.position import Position
from env.price_data import PriceData

class RealPosition(Position):
    """A position in the market.

    Positions with a deal_id are actual positions, a simulated one otherwise."""

    def __init__(self, amount: int, price_data: PriceData, price = None, deal_id = None, limit=None, stop=None):
        self.deal_id = deal_id
        super().__init__(amount, price, price_data, limit, stop)

    def __repr__(self):
        result = f"Real Position {self.deal_id} in {self.price_data.market_id} | {self.amount:.2f} @ {self.price:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

