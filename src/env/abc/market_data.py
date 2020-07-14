from abc import ABC


class MarketData(ABC):
    """This class stores and centrally updates price data for a single market."""

    def __init__(self, market_id, bid, ask, margin_req: float, lowest=None, highest=None):
        assert 0 < margin_req <= 1

        self.market_id = market_id
        self.margin_req = margin_req
        self.bid = bid
        self.ask = ask

        self.lowest = lowest or 0
        self.highest = highest

    def __repr__(self):
        return f"{self.__class__.__name__} '{self.market_id}' with prices " \
               f"{self.bid} / {self.ask} and margin of {self.margin_req}"
