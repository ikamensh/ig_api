from datetime import timedelta

import markets
from api.sim._sim_account import SimAccount


def test_long_order_converts(acc, price_data):
    price_data[markets.vix.code].set_prices(10, 11, 1)
    target_price = 5
    order = acc.create_order(markets.vix.code, amount=10, level=target_price)
    assert len(acc.orders) == 1
    assert len(acc.positions) == 0

    price_data[markets.vix.code].set_prices(low=3, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.orders) == 0
    assert len(acc.positions) == 1

    pos = acc.positions[0]
    assert pos.price == target_price


def test_short_order_converts(acc, price_data):
    price_data[markets.vix.code].set_prices(10, 11, 1)
    target_price = 20
    order = acc.create_order(markets.vix.code, amount=-10, level=target_price)
    assert len(acc.orders) == 1
    assert len(acc.positions) == 0

    price_data[markets.vix.code].set_prices(low=13, high=21, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.orders) == 0
    assert len(acc.positions) == 1

    pos = acc.positions[0]
    assert pos.price == target_price


def test_order_forwards_limit(acc, price_data):
    price_data[markets.vix.code].set_prices(10, 11, 1)
    target_price = 5
    limit = 20
    order = acc.create_order(markets.vix.code, amount=10, level=target_price, limit=limit)

    price_data[markets.vix.code].set_prices(low=3, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))

    pos = acc.positions[0]
    assert pos.limit == limit


def test_order_forwards_stop(acc, price_data):
    price_data[markets.vix.code].set_prices(10, 11, 1)
    target_price = 5
    stop = 2
    order = acc.create_order(markets.vix.code, amount=10, level=target_price, stop=stop)

    price_data[markets.vix.code].set_prices(low=3, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))

    pos = acc.positions[0]
    assert pos.stop == stop


def test_long_order_misses(acc, price_data):
    price_data[markets.vix.code].set_prices(10, 11, 1)
    target_price = 5
    order = acc.create_order(markets.vix.code, amount=10, level=target_price)
    assert len(acc.orders) == 1
    assert len(acc.positions) == 0

    price_data[markets.vix.code].set_prices(low=6, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.orders) == 1
    assert len(acc.positions) == 0


def test_short_order_misses(acc, price_data):
    price_data[markets.vix.code].set_prices(10, 11, 1)
    target_price = 20
    order = acc.create_order(markets.vix.code, amount=-10, level=target_price)
    assert len(acc.orders) == 1
    assert len(acc.positions) == 0

    price_data[markets.vix.code].set_prices(low=6, high=16, delta=1)
    acc.step(acc._last_date + timedelta(hours=3))
    assert len(acc.orders) == 1
    assert len(acc.positions) == 0
