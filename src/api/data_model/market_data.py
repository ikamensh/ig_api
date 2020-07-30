import markets


class MarketData:
    """This class stores and centrally updates price data for a single market."""

    def __init__(
        self,
        market_id: markets.MarketId,
        bid: float,
        ask: float,
        high: float,
        low: float,
        margin_req: float,
        time,
    ):
        assert 0 < margin_req <= 1

        self.market_id = market_id
        self.margin_req = margin_req
        self.bid = bid
        self.ask = ask

        self.delta = ask - bid
        self.high = high
        self.low = low

        self.time = time

    @property
    def low_bid(self):
        return self.low - self.delta / 2

    @property
    def high_bid(self):
        return self.high - self.delta / 2

    @property
    def low_ask(self):
        return self.low + self.delta / 2

    @property
    def high_ask(self):
        return self.high + self.delta / 2

    def __repr__(self):
        return (
            f"{self.__class__.__name__} '{self.market_id}' with prices "
            f"{self.bid} / {self.ask} and margin of {self.margin_req}"
        )
