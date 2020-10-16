from datetime import timedelta

from ig_api import markets


def test_hit_limit_long(acc, price_data):
    pos = acc.open(1000, markets.vix.code, limit=15)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=10, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 0


def test_miss_limit_long(acc, price_data):
    pos = acc.open(1000, markets.vix.code, limit=15)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=10, high=15, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 1


def test_hit_stop_long(acc, price_data):
    pos = acc.open(1000, markets.vix.code, stop=8)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=7, high=22, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 0


def test_miss_stop_long(acc, price_data):
    pos = acc.open(1000, markets.vix.code, stop=8)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=10, high=11, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 1


def test_hit_limit_short(acc, price_data):
    pos = acc.open(-1000, markets.vix.code, limit=5)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=4, high=16, delta=0.5)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 0


def test_miss_limit_short(acc, price_data):
    pos = acc.open(-1000, markets.vix.code, limit=5)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=7, high=14, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 1


def test_hit_stop_short(acc, price_data):
    pos = acc.open(-1000, markets.vix.code, stop=15)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(low=7, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 0


def test_miss_stop_short(acc, price_data):
    pos = acc.open(-1000, markets.vix.code, stop=15)
    assert len(acc.positions) == 1

    price_data[markets.vix.code].set_prices(9, 14, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.positions) == 1