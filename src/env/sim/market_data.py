from contextlib import contextmanager
from env.abc.market_data import MarketData


class SimMarket(MarketData):
    """This class stores and centrally updates price data for a single market."""

    def __init__(self, market_id, lowest=None, highest=None):
        self.high_bid = None
        self.high_ask = None

        self.low_bid = None
        self.low_ask = None

        self.step = 0

        super().__init__(
            market_id,
            bid=None,
            ask=None,
            margin_req=0.2,
            lowest=lowest,
            highest=highest,
        )

    def set_prices(self, low, high, delta):
        """Sets new price range. """
        assert low <= high
        self.low_ask = low + delta / 2
        self.low_bid = low - delta / 2

        self.high_ask = high + delta / 2
        self.high_bid = high - delta / 2

        self.bid = (self.high_bid + self.low_bid) / 2
        self.ask = (self.high_ask + self.low_ask) / 2
        self.step += 1

        if self.highest is None:
            self.highest = high * 10

    @contextmanager
    def moment_prices(self, bid, ask):
        """Use specific price between current min and max price."""
        old_ask, old_bid = self.ask, self.bid
        self.ask = min(self.high_ask, max(self.low_ask, ask))
        self.bid = min(self.high_bid, max(self.low_bid, bid))
        yield
        self.ask, self.bid = old_ask, old_bid
