from datetime import timedelta

from ig_api import markets


def test_holding_long_interest(acc):
    balance_init = 500
    acc.balance = balance_init
    pos = acc.open(10, markets.vix.code)

    for i in range(10):
        acc.step(acc._last_date + timedelta(hours=3))

    assert acc.balance != balance_init


def test_holding_short_interest(acc):
    balance_init = 500
    acc.balance = balance_init
    pos = acc.open(-10, markets.vix.code)

    for i in range(10):
        acc.step(acc._last_date + timedelta(hours=3))

    assert acc.balance != balance_init