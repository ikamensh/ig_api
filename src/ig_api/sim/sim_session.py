from datetime import datetime, timedelta
from typing import Generator, Tuple, List

from ig_api.abstract_session import Session
from ig_api.data_model.acc_detail import AccountDetails
from ig_api.data_model.order import Order
from ig_api.exceptions import MarketNotFoundError, OrderNotFoundError
from ig_api.datasets.market_history import MarketHistory
from ig_api.data_model.market_data import MarketData
from ig_api.data_model.position import Position
from ig_api.sim._sim_account import SimAccount
from ig_api.sim._sim_market_data import SimMarket


class SimServer:
    """Simulates the trading platform. """

    def __init__(self, balance: int, history: List[MarketHistory]):
        """Sim server will operate on the period of history where all markets have data."""

        common_window = max(h.start for h in history), min(h.end for h in history)
        history = [h.slice(*common_window) for h in history]

        self.market_history = {h.market.code: h for h in history}
        self.market_data = {h.market.code: SimMarket(h.market.code) for h in history}

        self._cur_time = common_window[0]
        self._set_prices()
        self.account = SimAccount(self.market_data, balance, self._cur_time)

    def price_history(
        self, market: str, resolution: str, start: datetime, end: datetime
    ):

        end = min(self._cur_time, end)
        # assert resolution == self.history.steps_per_day TODO
        for k, v in self.market_history[market].slice(start, end).items():
            yield (k, *v)

    def _set_prices(self):
        for k, v in self.market_data.items():
            low, high, delta = self.market_history[k][self._cur_time]
            v.set_prices(low, high, delta)

    def step(self, seconds):
        self._cur_time += timedelta(seconds=seconds)
        self._set_prices()
        self.account.step(self._cur_time)


class SimSession(Session):
    """A connection to a simulated server. Conforms the same API as real IgSession."""

    def __init__(self, server: SimServer):
        self._server = server
        self._market_data = {k: SimMarket(k) for k in server.market_data}

    def get_orders(self) -> List[Order]:
        return list(self._server.account.orders)

    def create_order(self, market: str, amount, level, limit=None, stop=None) -> Order:
        return self._server.account.create_order(market, amount, level, limit, stop)

    def delete_order(self, order: Order) -> None:
        try:
            self._server.account.orders.remove(order)
        except ValueError as e:
            raise OrderNotFoundError(f"Order is not found on the server: {order}") from e

    def get_positions(self) -> List[Position]:
        return list(self._server.account.positions)

    def get_market_data(self, market_code) -> MarketData:
        try:
            return self._market_data[market_code]
        except KeyError as e:
            raise MarketNotFoundError(f"Simulated Server has no historical data for market {market_code}") from e

    def update_market_data(self) -> None:
        for k, v in self._server.market_data.items():
            cached = self._market_data[k]
            if cached.time < v.time:
                cached.set_prices(v.low, v.high, v.delta, time=v.time)

    def open_position(
        self, market: str, amount: int, limit=None, stop=None
    ) -> Position:
        return self._server.account.open(amount, market, limit, stop)

    def close_position(self, pos: Position) -> None:
        self._server.account.close(pos)

    def get_acc_details(self) -> AccountDetails:
        return AccountDetails(
            balance=self._server.account.balance,
            profit_loss=self._server.account.profit(),
            available=self._server.account.available,
            name="Imaginary Account",
            id="12345",
            currency="Euro",
        )

    def price_history(
        self, market: str, resolution: str, start: datetime, end: datetime
    ) -> Generator[Tuple[str, float, float, float], None, None]:
        yield from self._server.price_history(market, resolution, start, end)
