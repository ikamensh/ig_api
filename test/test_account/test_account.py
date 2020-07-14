import pytest

from env.sim.account import SimAccount


@pytest.mark.parametrize("amount", [-50, 50])
def test_cycle_negative(amount, price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    a.close(pos)

    assert a.balance < balance_init
    assert not a.positions


@pytest.mark.parametrize("amount", [-50, 50])
def test_profit(amount, price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    price_data.change_price(amount//10)
    a.close(pos)

    assert a.balance > balance_init


@pytest.mark.parametrize("amount", [-50, 50])
def test_loss(amount, price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    price_data.change_price( - amount // 10)
    a.close(pos)

    assert a.balance < balance_init


def test_ensure_margin_long(price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000)
    assert len(a.positions) == 1

    price_data.set_prices(low=1, high=3)
    a.step()
    assert len(a.positions) == 0


def test_ensure_margin_short(price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000)
    assert len(a.positions) == 1

    price_data.set_prices(low=21, high=23)
    a.step()
    assert len(a.positions) == 0
