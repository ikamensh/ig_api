"""
add flag ` -m "not slow" ` to deselect slow tests.
"""

import pytest

from env.price_data import PriceData


class TestPriceData(PriceData):

    def change_price(self, delta):
        low = (self.low_bid + self.low_ask) / 2
        high = (self.high_bid + self.high_ask) / 2

        self.set_prices(low+delta, high+delta)


@pytest.fixture()
def price_data():
    p = TestPriceData(delta=1, market_id="vix", lowest=10, highest=110)
    p.set_prices(low=10, high=12)
    yield p