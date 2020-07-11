import pytest

from env.price_data import PriceData


@pytest.fixture()
def price_data():
    p = PriceData(delta=1)
    p.set_prices(low=10, high=12)
    yield p