import pytest

from src.robotrader.account import Platform


@pytest.fixture()
def platform():
    p = Platform()
    p.set_prices(low_bid=10, low_ask=11, high_bid=11, high_ask=12)
    yield p