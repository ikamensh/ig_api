import typing

from env.exceptions import InsufficientFundsException
from env.sim.market_data import SimMarket
from env.sim.position import SimPosition
from env.abc.account import Account

TAX_RATE = 0.30


class SimAccount(Account):
    """ Simulated account, performing taxation, ensuring the margin, etc.

    Currently supports only a single market positions defined by price_data.market"""
    positions: typing.List[SimPosition]

    def __init__(
            self,
            market_data: SimMarket,
            balance: float,
            steps_per_day: int,
            log: typing.List = None,
    ):
        super().__init__(balance, log)
        self.positions = []
        self.market_data = market_data
        self.steps_per_day = steps_per_day
        self.steps_counter = 0
        self.day = 0
        self.year_tax = 0
        self.year_start_balance = balance

    def _owed_tax(self):
        """Calculates how much tax is owed this year. """
        gain = self.balance - self.year_start_balance
        return gain * TAX_RATE

    def _settle_tax(self):
        """Pay / refund tax."""
        delta = self._owed_tax() - self.year_tax
        if delta > 0:
            self.balance -= delta
            self.year_tax += delta
        else:
            tax_return = min(-delta, self.year_tax)
            self.balance += tax_return
            self.year_tax -= tax_return

    def margin(self):
        """Minimum balance to keep all positions open. """
        return sum(p.margin() for p in self.positions)

    def profit(self, mode="market"):
        """Total profit / loss (negative profit) from all open positions. """
        return sum(p.profit(mode=mode) for p in self.positions)

    @property
    def available(self):
        """Free capital in the account. """
        return (
                self.balance
                + min(self.profit(mode) for mode in ["low", "high", "market"])
                - self.margin()
        )

    def open(self, amt: int, market="vix", limit=None, stop=None) -> SimPosition:
        """
        Open a new position at market price.

        Args:
            amt: amount, positive for long position and negative for short position
            limit: favorable price at which the position will be closed
            stop: unfavorable price at which the position will be closed

        Returns:
            the new position object
        """
        assert isinstance(amt, int)
        assert amt != 0

        pos = SimPosition(amt, self.market_data, limit=limit, stop=stop)
        if self.available >= pos.margin():
            self.positions.append(pos)
            if self.log is not None:
                self.log.append(f"Opening position {pos}")
                self.log.append(
                    f"balance {self.balance:.2f} | "
                    f"profit {self.profit():.2f} | available {self.available():.2f} | "
                    f"risk {self.risk():.2f} | margin {self.margin():.2f}"
                )
            return pos
        else:
            raise InsufficientFundsException

    def close(self, position: SimPosition):
        """Close a position at the market price."""

        assert position in self.positions
        profit = position.profit()
        if self.log is not None:
            self.log.append(f"Closing position {position} for {profit=:.2f}")
        self.balance += profit
        self.positions.remove(position)
        self._settle_tax()

    def step(self):
        """Time step. Should be called every time prices are updated."""
        self._ensure_margin()
        self.stop_limit()

        self.steps_counter += 1
        if not self.steps_counter % self.steps_per_day:
            self.steps_counter = 0
            self.day += 1
            days_to_pay = 1
            if not self.day % 7 == 5:
                days_to_pay += 2
                self.day += 2

            if self.day >= 365:
                self.year_tax = 0
                self.year_start_balance = self.balance
                self.day = 0

            for p in self.positions:
                self.balance -= days_to_pay * p.daily_cost()

    def stop_limit(self):
        """ Close positions according to set stops and limits. """
        for p in list(self.positions):
            if p.amount > 0:  # long
                if p.limit is not None and p.limit <= self.market_data.high_bid:
                    with self.market_data.moment_prices(
                            bid=p.limit, ask=p.limit + self.market_data.delta
                    ):
                        self.close(p)

                elif p.stop is not None and p.stop >= self.market_data.low_bid:
                    with self.market_data.moment_prices(
                            bid=p.stop, ask=p.stop + self.market_data.delta
                    ):
                        self.close(p)

            else:  # short
                if p.limit is not None and p.limit >= self.market_data.low_ask:
                    with self.market_data.moment_prices(
                            bid=p.limit - self.market_data.delta, ask=p.limit
                    ):
                        self.close(p)

                elif p.stop is not None and p.stop < self.market_data.high_ask:
                    with self.market_data.moment_prices(
                            bid=p.stop - self.market_data.delta, ask=p.stop
                    ):
                        self.close(p)

    def _ensure_margin(self):
        """Close positions until margin requirements are satisfied. """
        while self.available < 0 and self.positions:
            pos = self.positions[-1]
            self.close(pos)
