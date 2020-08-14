from abc import ABC

from robotrader.features.features import price
from src.robotrader.robotrader import RoboTrader


class PotentialTrader(RoboTrader, ABC):
    short_limit: float
    long_limit : float

    def __init__(self, account, market_data, steps_per_day):
        super().__init__(account, market_data, steps_per_day)

    def potential(self) -> float:
        """Potential is a number from -1 to 1.

        Potential means:
         0 means the bot thinks current price perfectly reflects the value of the asset;
         1 means that the asset is undervalued, it's great to own the asset.
        -1 means that asset is overvalued, it should be sold.
        """
        raise NotImplementedError

    def risk_factor(self) -> float:
        """ Risk factor is a factor from 0 to 1 describing how much risk the trader is willing to take.

        0 means margin is used as limitation to opening positions.
        1 means maximum risk is used as limitation to opening positions.
        """
        raise NotImplementedError

    def max_long_amount(self):
        risk_per_unit = self.market_data().ask - self.bounds.low(self.market)
        return self._limit(risk_per_unit)

    def max_short_amount(self):
        risk_per_unit = self.bounds.high(self.market) - self.market_data().bid
        return self._limit(risk_per_unit)

    def _limit(self, risk_per_unit):
        free_money = self.sess.get_acc_details().available - self._risk() * self.risk_factor()
        margin_per_unit = (
                self.market_data().margin_req
                * (self.market_data().bid + self.market_data().ask)
                / 2
        )
        limit = risk_per_unit * self.risk_factor() + margin_per_unit * (
                1 - self.risk_factor()
        )
        return free_money / limit

    def decide_actions(self):

        potential = self.potential()

        if potential > 0.1:
            buy_target = self.max_long_amount() * potential * potential

            if self.sess.get_positions() and self.sess.get_positions()[-1].amount < 0:
                closed = self._close_n(buy_target, potential)
                buy_target -= closed

            if buy_target > 0:
                self.open(int(buy_target + 1), limit=price(self.market_data()) * (1 + self.long_limit))

        elif potential < -0.1:
            sell_target = self.max_short_amount() * potential * potential

            if self.positions and self.positions[-1].amount > 0:
                closed = self._close_n(sell_target, potential)
                sell_target -= closed

            if sell_target > 0:
                self.open(-int(sell_target + 1), limit=price(self.market_data()) * (1 - self.short_limit) )

    def _close_n(self, base_amount, potential):

        amt = abs(sum(p.amount for p in self.positions))
        close_max = self.market_data().ask * amt
        close_target = close_max * potential * potential + base_amount
        closed = 0
        while self.positions and closed < close_target:
            p = self.positions[-1]
            self.close(p)
            closed += abs(p.amount)
        return closed
