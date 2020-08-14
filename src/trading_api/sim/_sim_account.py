import collections
import typing
from contextlib import contextmanager
from datetime import datetime

from trading_api.data_model.order import Order
from trading_api.exceptions import InsufficientFundsException

from loguru import logger

from trading_api.data_model.position import Position
import markets
from trading_api.sim._sim_market_data import SimMarket


@contextmanager
def _moment_prices(self, bid, ask):
    """Use specific price between current min and max price."""
    old_ask, old_bid = self.ask, self.bid
    self.ask = min(self.high_ask, max(self.low_ask, ask))
    self.bid = min(self.high_bid, max(self.low_bid, bid))
    yield
    self.ask, self.bid = old_ask, old_bid

class SimAccount:
    """ Simulated account, performing taxation, ensuring the margin, etc.

    Currently supports only a single market positions defined by price_data.market"""

    TAX_RATE = 0.30
    long_interest_rate: typing.Dict[str, float] = {markets.vix.code: 1 / 1500}
    short_interest_rate: typing.Dict[str, float] = {markets.vix.code: -1 / 1000}

    def __init__(
        self, market_data: typing.Dict[str, SimMarket], balance: float, start_date: datetime
    ):
        self.balance = balance
        self.positions: typing.List[Position] = []
        self.orders: typing.List[Order] = []
        self.market_data = market_data
        self._last_date = start_date
        self.year_tax = 0
        self.year_start_balance = balance
        self._margin = None
        self._profit = None
        self._orders_counter = 0
        self._positions_counter = 0

    def assets(self) -> typing.Dict[str, int]:
        """Total amount of the assets bought across all positions (negative for shorts).

         Is represented as a dictionary from a market code to the total asset."""
        assets = collections.defaultdict(int)

        for p in self.positions:
            assets[p.market_data.market_code] += p.amount

        return assets

    def _owed_tax(self):
        """Calculates how much tax is owed this year. """
        gain = self.balance - self.year_start_balance
        return gain * self.TAX_RATE

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
        if self._margin is None:
            result = sum(p.margin() for p in self.positions)
            result += sum(o.margin() for o in self.orders)
            self._margin = result
        return self._margin

    def profit(self):
        """Total profit / loss (negative profit) from all open positions. """
        if self._profit is None:
            self._profit = sum(p.profit() for p in self.positions)
        return self._profit

    @property
    def available(self):
        """Free capital in the account. """
        return self.balance + self.profit() - self.margin()

    def create_order(self, market_code, amount, level, limit=None, stop=None) -> Order:
        order = Order(
            market_code, amount, level, limit, stop, deal_id=str(self._orders_counter)
        )
        self._orders_counter += 1

        if self.available > order.margin():
            self.orders.append(order)
            return order
        else:
            raise InsufficientFundsException

    def open(
        self, amt: int, market, limit=None, stop=None
    ) -> Position:
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
        market_data = self.market_data[market]

        price = market_data.ask if amt > 0 else market_data.bid

        pos = Position(
            amt,
            market_data,
            price,
            limit=limit,
            stop=stop,
            deal_id=self._next_pos_id(),
        )
        if self.available >= pos.margin():
            self.positions.append(pos)
            self._profit = None
            self._margin = None
            logger.info(f"Opening position {pos}")
            logger.debug(
                f"balance {self.balance:.2f} | profit {self.profit():.2f} | "
                f"available {self.available:.2f} |  margin {self.margin():.2f}"
            )
            return pos
        else:
            raise InsufficientFundsException

    def _next_pos_id(self):
        deal_id = f"Sim Deal {self._positions_counter}"
        self._positions_counter += 1
        return deal_id

    def close(self, position: Position):
        """Close a position at the market price."""

        assert position in self.positions
        profit = position.profit()
        logger.info(f"Closing position {position} for {profit=:.2f}")
        self.balance += profit
        self.positions.remove(position)
        self._profit = None
        self._margin = None
        self._settle_tax()

    def step(self, new_date: datetime):
        """Time step. Should be called every time prices are updated."""
        self._profit = None
        self._margin = None

        self._ensure_margin()
        self._process_stop_limit()

        self._collect_interest(new_date)
        self._process_orders()
        assert new_date >= self._last_date
        if new_date.year > self._last_date.year:
            self.year_tax = 0
            self.year_start_balance = self.balance
        self._last_date = new_date

    def _collect_interest(self, new_date: datetime):
        """ Depends on correct date being already set. """

        elapsed = new_date - self._last_date
        days_to_pay = elapsed.total_seconds() / 86_400

        for p in self.positions:
            self.balance -= days_to_pay * self._daily_cost(p)

    def _daily_cost(self, pos: Position):
        """ Calculate cost of holding a position open for a day. """

        ask, bid = pos.market_data.ask, pos.market_data.bid
        value = abs(pos.amount) * (ask + bid) / 2
        if pos.amount > 0:
            return value * self.long_interest_rate[pos.market_code]
        else:
            return value * self.short_interest_rate[pos.market_code]

    def _process_stop_limit(self):
        """ Close positions according to set stops and limits. """
        for p in list(self.positions):
            if p.amount > 0:  # long
                if p.limit is not None and p.limit <= p.market_data.high_bid:
                    with _moment_prices( p.market_data, bid=p.limit, ask=p.limit):
                        self.close(p)

                elif p.stop is not None and p.stop >= p.market_data.low_bid:
                    with _moment_prices( p.market_data, bid=p.stop, ask=p.stop):
                        self.close(p)

            else:  # short
                if p.limit is not None and p.limit >= p.market_data.low_ask:
                    with _moment_prices( p.market_data, bid=p.limit, ask=p.limit):
                        self.close(p)

                elif p.stop is not None and p.stop < p.market_data.high_ask:
                    with _moment_prices( p.market_data, bid=p.stop, ask=p.stop):
                        self.close(p)

    def _ensure_margin(self):
        """Close positions until margin requirements are satisfied. """
        while self.available < 0 and self.orders:
            self.orders.pop()

        while self.available < 0 and self.positions:
            pos = self.positions[-1]
            self.close(pos)

    def _process_orders(self) -> None:
        """ Open positions for orders if desired price is available. """
        converted = []

        def convert(order, price):
            market_data = self.market_data[order.market_code]
            p = Position(
                order.amount,
                market_data,
                price,
                deal_id=self._next_pos_id(),
                limit=order.limit,
                stop=order.stop,
            )
            self.positions.append(p)
            converted.append(order)

        for o in self.orders:
            market_data = self.market_data[o.market_code]
            if o.amount > 0:
                best_price = market_data.low_ask
                if o.level >= best_price:
                    price = min(market_data.high_ask, o.level)
                    convert(o, price)
            else:
                best_price = market_data.high_bid
                if o.level <= best_price:
                    price = max(market_data.low_bid, o.level)
                    convert(o, price)

        for o in converted:
            self.orders.remove(o)
