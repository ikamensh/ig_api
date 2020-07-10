import pytest

from src.robotrader.account import Platform


@pytest.fixture()
def platform():
    p = Platform(delta=1)
    p.set_prices(low=10, high=12)
    yield p