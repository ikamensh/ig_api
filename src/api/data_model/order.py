class Order:
    """ Order represents request to the platform to do a trade at desired price.

    Naturally, the desired price might never become available, so order has no defined completion date.
    Note that the desired price must be better than the current price to place an order.
    """

    def __init__(
        self, market_code: str, amount: int, level, limit=None, stop=None, deal_id=None
    ):
        self.market_code = market_code
        self.amount = amount
        self.level = level
        self.limit = limit
        self.stop = stop
        self.deal_id = deal_id

    def __repr__(self):
        result = f"Order {self.deal_id} in {self.market_code} | {self.amount:.2f} @ {self.level:.2f}"
        if self.limit:
            result += f" limit: {self.limit}"
        if self.stop:
            result += f" stop: {self.stop}"
        return result

    def __eq__(self, other):
        if not isinstance(other, Order):
            return False

        if self.deal_id == other.deal_id:
            assert self.amount == other.amount
            assert self.market_code == other.market_code
            return True

        return False

    def __hash__(self):
        return hash(self.deal_id)

    def margin(self):
        """Minimum balance to keep this order open. """
        return self.level * abs(self.amount)
