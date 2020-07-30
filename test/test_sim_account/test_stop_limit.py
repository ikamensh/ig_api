from sim._sim_account import SimAccount


def test_hit_limit_long(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    price_data.set_prices(low=10, high=16, delta=1)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_long(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, limit=15)
    assert len(a.positions) == 1

    price_data.set_prices(low=10, high=15, delta=1)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_long(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    price_data.set_prices(low=7, high=22, delta=1)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_long(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(1000, stop=8)
    assert len(a.positions) == 1

    price_data.set_prices(low=10, high=11, delta=1)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_limit_short(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    price_data.set_prices(low=4, high=16, delta=0.5)
    a.step()
    assert len(a.positions) == 0
    assert a.balance > balance_init


def test_miss_limit_short(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, limit=5)
    assert len(a.positions) == 1

    price_data.set_prices(low=7, high=14, delta=1)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init


def test_hit_stop_short(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    price_data.set_prices(low=7, high=16, delta=1)
    a.step()
    assert len(a.positions) == 0
    assert a.balance < balance_init


def test_miss_stop_short(price_data):
    balance_init = 5_000_000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(-1000, stop=15)
    assert len(a.positions) == 1

    price_data.set_prices(9, 14, delta=1)
    a.step()
    assert len(a.positions) == 1
    assert a.balance == balance_init