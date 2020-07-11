import pytest

from env.account import Account


@pytest.mark.parametrize("amount", [-50, 50])
def test_cycle_negative(amount, price_data):

    balance_init = 5000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    a.close(pos)

    assert a.balance < balance_init
    assert not a.positions


def test_ensure_margin_long(price_data):

    balance_init = 5000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000)
    assert len(a.positions) == 1

    price_data.set_prices(low=1, high=3)
    a.step()
    assert len(a.positions) == 0


def test_ensure_margin_short(price_data):
    balance_init = 5000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000)
    assert len(a.positions) == 1

    price_data.set_prices(low=21, high=23)
    a.step()
    assert len(a.positions) == 0


def test_hit_limit_long(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    price_data.set_prices(low=10, high=16)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_long(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    price_data.set_prices(low=10, high=15)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_long(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    price_data.set_prices(low=7, high=22)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_long(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    price_data.set_prices(low=10, high=11)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_limit_short(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    price_data.set_prices(low=4, high=16)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_short(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    price_data.set_prices(low=7, high=14)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_short(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    price_data.set_prices(low=7, high=16)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_short(price_data):
    balance_init = 5_000_000
    a = Account(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    price_data.set_prices(9, 14)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_holding_long_costs(price_data):
    STEPS_PER_DAY = 4
    balance_init = 500
    a = Account(price_data, balance=balance_init, steps_per_day=STEPS_PER_DAY)
    pos = a.open(10)

    for i in range(STEPS_PER_DAY*10):
        a.step()

    assert a.balance < balance_init


def test_holding_short_costs(price_data):
    STEPS_PER_DAY = 4
    balance_init = 500
    a = Account(price_data, balance=balance_init, steps_per_day=STEPS_PER_DAY)
    pos = a.open(-10)

    for i in range(STEPS_PER_DAY * 10):
        a.step()

    assert a.balance < balance_init

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

