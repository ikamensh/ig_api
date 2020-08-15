from datetime import datetime
import typing

from trading_api.data_model.snapshot import Snapshot, MarketStatus


class MarketData:
    """This class stores and centrally updates price data for a single market."""

    def __init__(
        self,
        market_code: str,
        bid: float,
        ask: float,
        high: float,
        low: float,
        margin_req: float,
        time,
    ):
        assert 0 < margin_req <= 1

        self.market_code = market_code
        self.margin_req = margin_req
        self.bid = bid
        self.ask = ask

        self.delta = ask - bid  # spread
        self.high = high
        self.low = low

        self.time = time
        self.status = MarketStatus.EDITS

    @staticmethod
    def from_snapshot(
        snap: Snapshot, market_code: str, margin_req: float
    ) -> "MarketData":
        result = MarketData(
            market_code=market_code,
            bid=snap.bid,
            ask=snap.offer,
            low=snap.low,
            high=snap.high,
            margin_req=margin_req,
            time=datetime.now(),
        )
        result.status = snap.status
        return result

    def update(self, snap: Snapshot):
        self.bid = snap.bid
        self.ask = snap.offer
        self.low = snap.low
        self.high = snap.high
        self.time = datetime.now()

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
            f"{self.__class__.__name__} '{self.market_code}' with prices "
            f"{self.bid} / {self.ask} and margin of {self.margin_req}"
        )
