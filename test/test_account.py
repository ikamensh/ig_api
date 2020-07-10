import pytest

from src.robotrader.account import Account


@pytest.mark.parametrize("amount", [-50, 50])
def test_cycle_negative(amount, platform):

    balance_init = 5000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    a.close(pos)

    assert a.balance < balance_init
    assert not a.positions


def test_ensure_margin_long(platform):

    balance_init = 5000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000)
    assert len(a.positions) == 1

    platform.set_prices(low=1, high=3)
    a.step()
    assert len(a.positions) == 0


def test_ensure_margin_short(platform):
    balance_init = 5000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000)
    assert len(a.positions) == 1

    platform.set_prices(low=21, high=23)
    a.step()
    assert len(a.positions) == 0


def test_hit_limit_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    platform.set_prices(low=10, high=16)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    platform.set_prices(low=10, high=15)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    platform.set_prices(low=7, high=22)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    platform.set_prices(low=10, high=11)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_limit_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    platform.set_prices(low=4, high=16)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    platform.set_prices(low=7, high=14)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    platform.set_prices(low=7, high=16)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    platform.set_prices(9,14)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_holding_long_costs(platform):
    STEPS_PER_DAY = 4
    balance_init = 500
    a = Account(platform, balance=balance_init, steps_per_day=STEPS_PER_DAY)
    pos = a.open(10)

    for i in range(STEPS_PER_DAY*10):
        a.step()

    assert a.balance < balance_init


def test_holding_short_costs(platform):
    STEPS_PER_DAY = 4
    balance_init = 500
    a = Account(platform, balance=balance_init, steps_per_day=STEPS_PER_DAY)
    pos = a.open(-10)

    for i in range(STEPS_PER_DAY * 10):
        a.step()

    assert a.balance < balance_init
