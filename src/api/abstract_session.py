from abc import ABC
from datetime import datetime
from typing import List, Generator, Tuple

from api.data_model.acc_detail import AccountDetails
from api.data_model.market_data import MarketData
from api.data_model.position import Position


class Session(ABC):

    def get_positions(self) -> List[Position]:
        raise NotImplementedError

    def get_market_data(self, market_code) -> MarketData:
        raise NotImplementedError

    def update_market_data(self) -> None:
        raise NotImplementedError

    def open_position(self, amount: int, market: str, limit=None, stop=None) -> Position:
        raise NotImplementedError

    def close_position(self, pos: Position) -> None:
        raise NotImplementedError

    def get_acc_details(self) -> AccountDetails:
        raise NotImplementedError

    def price_history(
        self, market: str, resolution: str, start: datetime, end: datetime,
    ) -> Generator[Tuple[str, float, float, float], None, None]:
        raise NotImplementedError
