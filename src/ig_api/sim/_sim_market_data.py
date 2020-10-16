from contextlib import contextmanager
import datetime

from ig_api.data_model.market_data import MarketData


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

    def set_prices(self, low, high, delta, time = None):
        """Sets new price range. """
        assert low <= high
        assert delta >= 0

        self.delta = delta
        self.high = high
        self.low = low

        middle = (low + high) / 2

        self.bid = middle - delta / 2
        self.ask = middle + delta / 2
        if time is None:
            self.time += datetime.timedelta(days=1)
        else:
            self.time = time
