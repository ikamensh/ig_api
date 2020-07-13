import pytest

from env.sim.account import Account


@pytest.mark.parametrize("amount", [-50, 50])
def test_positive_risk(amount, price_data):
    balance_init = 5000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    assert a.risk() > 0


@pytest.mark.parametrize("amount", [-50, 50])
def test_risk_proportional(amount, price_data):
    balance_init = 5000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos1 = a.open(amount)
    pos2 = a.open(amount * 2)
    assert pos1.risk() < pos2.risk()


@pytest.mark.parametrize("amount", [-50, 50])
def test_risk_smaller_for_good_price(amount, price_data):
    balance_init = 5000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    price_data.set_prices(low=10, high=12)
    pos1 = a.open(amount)
    d_price = amount / 10
    # price changes in unfavorable direction
    price_data.set_prices(low=10 + d_price, high=12 + d_price)
    pos2 = a.open(amount)
    assert pos1.risk() < pos2.risk()