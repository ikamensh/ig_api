import typing
import datetime

from loguru import logger

from api.ig_session import IgSession
from env.abc.account import Account
from env.real.position import RealPosition



class RealAccount(Account):
    available: float
    positions: typing.List[RealPosition]

    def __init__(
            self,
            sess: IgSession,
    ):
        self.sess = sess
        self.update_time = datetime.datetime.now()
        acc_details = sess.get_acc_details()
        self._positions = None
        self._profit = acc_details.profit_loss
        super().__init__(acc_details.balance)

    @property
    def positions(self):
        if self._positions is None:
            self._positions = self.sess.get_positions()
        return self._positions

    def profit(self):
        """Total profit / loss (negative profit) from all open positions. """
        return self._profit

    def open(self, amt: int, market: str, limit=None, stop=None) -> RealPosition:
        """
        Open a new position at market price.

        Args:
            market: market identifier ("epic", e.g. "CS.D.CFEGOLD.CFE.IP" for gold)
            amt: amount, positive for long position and negative for short position
            limit: favorable price at which the position will be closed
            stop: unfavorable price at which the position will be closed

        Returns:
            the new position object
        """
        pos = self.sess.open_position(amt, market)
        self.positions.append(pos)
        logger.info(f"Opened position {pos}")
        return pos

    def close(self, position: RealPosition):
        """Close a position at the market price."""
        self.sess.close_position(position)
        self.positions.remove(position)
        logger.info(f"Closed position {position}")

    def step(self):
        self._positions = None
        self.update_time = datetime.datetime.now()
        acc_details = self.sess.get_acc_details()
        # TODO delete price data in sess?
        self._profit = acc_details.profit_loss
        self.balance = acc_details.balance
