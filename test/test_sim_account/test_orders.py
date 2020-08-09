from api.sim._sim_account import SimAccount


def test_long_order_converts(price_data):
    a = SimAccount(price_data, balance=5_000, steps_per_day=100)
    price_data.set_prices(10, 11, 1)
    target_price = 5
    order = a.create_order(price_data.market_code, amount=10, level=target_price)
    assert len(a.orders) == 1
    assert len(a.positions) == 0

    price_data.set_prices(low=3, high=16, delta=1)
    a.step()
    assert len(a.orders) == 0
    assert len(a.positions) == 1

    pos = a.positions[0]
    assert pos.price == target_price


def test_short_order_converts(price_data):
    a = SimAccount(price_data, balance=5_000, steps_per_day=100)
    price_data.set_prices(10, 11, 1)
    target_price = 20
    order = a.create_order(price_data.market_code, amount=-10, level=target_price)
    assert len(a.orders) == 1
    assert len(a.positions) == 0

    price_data.set_prices(low=13, high=21, delta=1)
    a.step()
    assert len(a.orders) == 0
    assert len(a.positions) == 1

    pos = a.positions[0]
    assert pos.price == target_price


def test_order_forwards_limit(price_data):
    a = SimAccount(price_data, balance=5_000, steps_per_day=100)
    price_data.set_prices(10, 11, 1)
    target_price = 5
    limit = 20
    order = a.create_order(price_data.market_code, amount=10, level=target_price, limit=limit)

    price_data.set_prices(low=3, high=16, delta=1)
    a.step()

    pos = a.positions[0]
    assert pos.limit == limit


def test_order_forwards_stop(price_data):
    a = SimAccount(price_data, balance=5_000, steps_per_day=100)
    price_data.set_prices(10, 11, 1)
    target_price = 5
    stop = 2
    order = a.create_order(price_data.market_code, amount=10, level=target_price, stop=stop)

    price_data.set_prices(low=3, high=16, delta=1)
    a.step()

    pos = a.positions[0]
    assert pos.stop == stop


def test_long_order_misses(price_data):
    a = SimAccount(price_data, balance=5_000, steps_per_day=100)
    price_data.set_prices(10, 11, 1)
    target_price = 5
    order = a.create_order(price_data.market_code, amount=10, level=target_price)
    assert len(a.orders) == 1
    assert len(a.positions) == 0

    price_data.set_prices(low=6, high=16, delta=1)
    a.step()
    assert len(a.orders) == 1
    assert len(a.positions) == 0


def test_short_order_misses(price_data):
    a = SimAccount(price_data, balance=5_000, steps_per_day=100)
    price_data.set_prices(10, 11, 1)
    target_price = 20
    order = a.create_order(price_data.market_code, amount=-10, level=target_price)
    assert len(a.orders) == 1
    assert len(a.positions) == 0

    price_data.set_prices(low=6, high=16, delta=1)
    a.step()
    assert len(a.orders) == 1
    assert len(a.positions) == 0
