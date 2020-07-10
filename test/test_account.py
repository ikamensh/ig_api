import pytest

from src.robotrader.account import Platform, Account


@pytest.fixture()
def platform():
    p = Platform()
    p.set_prices(low_bid=10, low_ask=11, high_bid=11, high_ask=12)
    yield p


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

    platform.set_prices(low_bid=1, low_ask=2, high_bid=2, high_ask=3)
    a.step()
    assert len(a.positions) == 0


def test_ensure_margin_short(platform):
    balance_init = 5000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=21, low_ask=22, high_bid=22, high_ask=23)
    a.step()
    assert len(a.positions) == 0


def test_hit_limit_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=9, low_ask=10, high_bid=16, high_ask=17)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=9, low_ask=10, high_bid=14, high_ask=15.1)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=7, low_ask=8, high_bid=22, high_ask=23)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_long(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=9, low_ask=10, high_bid=10, high_ask=11)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_limit_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=4, low_ask=5, high_bid=16, high_ask=17)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=6, low_ask=7, high_bid=14, high_ask=15.1)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=7, low_ask=8, high_bid=22, high_ask=23)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_short(platform):
    balance_init = 5_000_000
    a = Account(platform, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    platform.set_prices(low_bid=9, low_ask=10, high_bid=13, high_ask=14)
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
