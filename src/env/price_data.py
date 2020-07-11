from contextlib import contextmanager


class PriceData:
    """This class stores and centrally updates price data for a single market."""

    def __init__(self, delta):
        """
        Args:
            delta: difference between buying and selling price in the market.
        """
        self.high_bid = None
        self.high_ask = None

        self.low_bid = None
        self.low_ask = None

        self.market_ask = None
        self.market_bid = None
        self.delta = delta
        self.step = 0

    def set_prices(self, low, high):
        """Sets new price range. """
        assert low <= high
        self.low_ask = low + self.delta / 2
        self.low_bid = low - self.delta / 2

        self.high_ask = high + self.delta / 2
        self.high_bid = high - self.delta / 2

        self.market_bid = (self.high_bid + self.low_bid) / 2
        self.market_ask = (self.high_ask + self.low_ask) / 2
        self.step += 1

    @contextmanager
    def moment_prices(self, bid, ask):
        """Use specific price between current min and max price."""
        old_ask, old_bid = self.market_ask, self.market_bid
        self.market_ask = min(self.high_ask, max(self.low_ask, ask))
        self.market_bid = min(self.high_bid, max(self.low_bid, bid))
        yield
        self.market_ask, self.market_bid = old_ask, old_bid