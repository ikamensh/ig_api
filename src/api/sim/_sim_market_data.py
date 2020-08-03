from contextlib import contextmanager
import datetime

from api.data_model.market_data import MarketData


class SimMarket(MarketData):
    """This class stores and centrally updates price data for a single market."""

    def __init__(self, market_code):
        super().__init__(
            market_code,
            bid=0,
            ask=0,
            low=0,
            high=0,
            margin_req=0.2,
            time=datetime.datetime(year=1971, month=1, day=1),
        )

    def set_prices(self, low, high, delta):
        """Sets new price range. """
        assert low <= high
        assert delta >= 0

        self.delta = delta
        self.high = high
        self.low = low

        middle = (low + high) / 2

        self.bid = middle - delta / 2
        self.ask = middle + delta / 2
        self.time += datetime.timedelta(days=1)


    @contextmanager
    def moment_prices(self, bid, ask):
        """Use specific price between current min and max price."""
        old_ask, old_bid = self.ask, self.bid
        self.ask = min(self.high_ask, max(self.low_ask, ask))
        self.bid = min(self.high_bid, max(self.low_bid, bid))
        yield
        self.ask, self.bid = old_ask, old_bid
