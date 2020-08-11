from datetime import timedelta

import pytest

import markets

@pytest.mark.parametrize("amount", [-50, 50])
def test_cycle_negative(amount, acc):
    balance_init = 5000
    pos = acc.open(amount, markets.vix.code)
    acc.close(pos)

    assert acc.balance < balance_init
    assert not acc.positions


@pytest.mark.parametrize("amount", [-50, 50])
def test_profit(amount, price_data, acc):
    balance_init = 5000
    pos = acc.open(amount, markets.vix.code)
    price_data[markets.vix.code].change_price(amount//10)
    acc.close(pos)

    assert acc.balance > balance_init


@pytest.mark.parametrize("amount", [-50, 50])
def test_loss(amount, price_data, acc):
    balance_init = 5000
    acc.balance = balance_init
    pos = acc.open(amount, markets.vix.code)
    price_data[markets.vix.code].change_price( - amount // 10)
    acc.close(pos)

    assert acc.balance < balance_init


def test_ensure_margin_long(price_data, acc):
    pos = acc.open(1000, markets.vix.code)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=1, high=3, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 0


def test_ensure_margin_short(price_data, acc):
    pos = acc.open(-1000, markets.vix.code)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=21, high=23, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 0
