import typing

from env.exceptions import InsufficientFundsException
from env.position import Position
from env.price_data import PriceData

TAX_RATE = 0.25

class Account:
    def __init__(self, platform: PriceData, balance: float, steps_per_day: int, log: typing.List = None):
        self.balance = balance
        self.positions: typing.List[Position] = []
        self.pform = platform
        self.steps_per_day = steps_per_day
        self.steps_counter = 0
        self.day = 0
        self.log = log

        self.year_tax = 0
        self.year_start_balance = balance

    def owed_tax(self):
        gain = self.balance - self.year_start_balance
        return gain * TAX_RATE

    def settle_tax(self):
        delta = self.owed_tax() - self.year_tax
        if delta > 0:
            self.balance -= delta
            self.year_tax += delta
        else:
            tax_return = min( -delta, self.year_tax)
            self.balance += tax_return
            self.year_tax -= tax_return

    def margin(self):
        return sum(p.margin() for p in self.positions)

    def profit(self, mode="market"):
        return sum(p.profit(mode=mode) for p in self.positions)

    def available(self):
        return min(
            self.balance + self.profit(mode) - self.margin()
            for mode in ["low", "high", "market"]
        )

    def risk(self):
        return sum(p.risk() for p in self.positions)

    def asset(self):
        return sum(p.amount for p in self.positions)

    def open(self, amt, limit = None, stop = None) -> Position:
        pos = Position(amt, self.pform, limit=limit, stop=stop)
        if self.available() >= pos.margin():
            self.positions.append(pos)
            if self.log is not None:
                self.log.append(f"Opening position {pos}")
                self.log.append(f"balance {self.balance:.2f} | asset {self.asset():.2f} | "
                                f"profit {self.profit():.2f} | available {self.available():.2f} | "
                                f"risk {self.risk():.2f} | margin {self.margin():.2f}")
            return pos
        else:
            raise InsufficientFundsException

    def close(self, position: Position):
        assert position in self.positions
        profit = position.profit()
        if self.log is not None:
            self.log.append(f"Closing position {position} for {profit=:.2f}")
        self.balance += profit
        self.positions.remove(position)
        self.settle_tax()

    def step(self):
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
        for p in list(self.positions):
            if p.amount > 0:  # long
                if p.limit is not None and p.limit <= self.pform.high_bid:
                    with self.pform.moment_prices(
                            bid=p.limit, ask=p.limit + self.pform.delta
                    ):
                        self.close(p)

                elif p.stop is not None and p.stop >= self.pform.low_bid:
                    with self.pform.moment_prices(
                            bid=p.stop, ask=p.stop + self.pform.delta
                    ):
                        self.close(p)

            else:  # short
                if p.limit is not None and p.limit >= self.pform.low_ask:
                    with self.pform.moment_prices(
                            bid=p.limit - self.pform.delta, ask=p.limit
                    ):
                        self.close(p)

                elif p.stop is not None and p.stop < self.pform.high_ask:
                    with self.pform.moment_prices(
                            bid=p.stop - self.pform.delta, ask=p.stop
                    ):
                        self.close(p)

    def _ensure_margin(self):
        while self.available() < 0 and self.positions:
            pos = self.positions[-1]
            self.close(pos)
