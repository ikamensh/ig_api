from env.sim.account import Account


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