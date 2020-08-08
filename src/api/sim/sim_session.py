from datetime import datetime
from typing import Generator, Tuple, List

from api.abstract_session import Session
from api.data_model.acc_detail import AccountDetails
from api.data_model.order import Order
from datasets.market_history import MarketHistory
from api.data_model.market_data import MarketData
from api.data_model.position import Position
from api.sim._sim_account import SimAccount
from api.sim._sim_market_data import SimMarket


class SimulatedServer:
    """Simulates the trading platform. """

    def __init__(self, balance: int, history: MarketHistory):
        self.history = history
        self.steps_iter = iter(history.keys())
        self.market_data = SimMarket(history.market.code)
        self.cur_time = next(self.steps_iter)
        self._set_prices()
        self.account = SimAccount(
            self.market_data, balance, steps_per_day=history.steps_per_day
        )

    def price_history(
        self, market: str, resolution: str, start: datetime, end: datetime
    ):
        assert market == self.history.market.code

        end = min(self.cur_time, end)
        # assert resolution == self.history.steps_per_day TODO
        for k, v in self.history.slice(start, end).items():
            yield (k.isoformat(), *v)

    def _set_prices(self):
        low, high, delta = self.history[self.cur_time]
        self.market_data.set_prices(low, high, delta)

    def step(self):
        self.cur_time = next(self.steps_iter)
        self._set_prices()
        self.account.step()


class SimSession(Session):
    """A connection to a simulated server. Conforms the same API as real IgSession."""

    def get_orders(self) -> List[Order]:
        return list(self._server.account.orders)

    def create_order(self, market: str, amount, level, limit=None, stop=None) -> Order:
        return self._server.account.create_order(market, amount, level, limit, stop)

    def delete_order(self, order: Order) -> None:
        self._server.account.orders.remove(order)

    def __init__(self, server: SimulatedServer):
        self._server = server
        self._market_data = SimMarket(server.market_data.market_code)

    def get_positions(self) -> List[Position]:
        return list(self._server.account.positions)

    def get_market_data(self, market_code) -> MarketData:
        assert market_code == self._server.market_data.market_code
        return self._market_data

    def update_market_data(self) -> None:
        if self._market_data.time <  self._server.market_data.time:
            src = self._server.market_data
            self._market_data.set_prices(src.low, src.high, src.delta, time=src.time)

    def open_position(
        self, amount: int, market: str, limit=None, stop=None
    ) -> Position:
        assert market == self._server.market_data.market_code
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
