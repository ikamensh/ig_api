import collections
import typing

from env.sim.position import Position
from abc import ABC


class Account(ABC):
    available: float

    def __init__(
            self,
            balance: float,
            log: typing.List = None,
    ):
        self.balance = balance
        self.positions: typing.List[Position] = []
        self.log = log

    def margin(self):
        """Minimum balance to keep all positions open. """
        return sum(p.margin() for p in self.positions)

    def profit(self, *args, **kwargs):
        """Total profit / loss (negative profit) from all open positions. """
        raise NotImplementedError

    def risk(self) -> float:
        """How much money can be lost given open positions in the worst case scenario?"""
        return sum(p.risk() for p in self.positions)

    def assets(self) -> typing.Dict[str, int]:
        """Total amount of the assets bought across all positions (negative for shorts).

         Is represented as a dictionary from a market code to the total asset."""
        assets = collections.defaultdict(int)

        for p in self.positions:
            assets[p.market_data.market_id] += p.amount

        return assets

    def open(self, amt: int, market: str, limit=None, stop=None) -> Position:
        """
        Open a new position at market price.

        Args:
            amt: amount, positive for long position and negative for short position
            limit: favorable price at which the position will be closed
            stop: unfavorable price at which the position will be closed

        Returns:
            the new position object
        """
        raise NotImplementedError

    def close(self, position: Position):
        """Close a position at the market price."""
        raise NotImplementedError

    def step(self):
        raise NotImplementedError
