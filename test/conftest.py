"""
add flag ` -m "not slow" ` to deselect slow tests.
"""

import pytest

from api.sim._sim_market_data import SimMarket


class TestMarketData(SimMarket):

    def change_price(self, change, delta = 1):
        low = (self.low_bid + self.low_ask) / 2
        high = (self.high_bid + self.high_ask) / 2

        self.set_prices(low + change, high + change, delta)


@pytest.fixture()
def price_data():
    p = TestMarketData(market_id="vix")
    p.set_prices(low=10, high=12, delta=1)
    yield p