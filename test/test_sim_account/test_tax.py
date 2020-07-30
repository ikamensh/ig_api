import pytest

from sim._sim_account import SimAccount

@pytest.mark.parametrize("amount", [-50, 50])
def test_profit(amount, price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)
    assert a.year_tax == 0

    price_data.change_price(amount//10)
    profit = pos.profit()
    a.close(pos)

    assert balance_init + profit > balance_init
    assert a.year_tax > 0


@pytest.mark.parametrize("amount", [-50, 50])
def test_loss_compensation(amount, price_data):

    paid_tax = 1000
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    a.year_tax = paid_tax
    pos = a.open(amount)

    price_data.change_price( - amount // 10)
    loss = -pos.profit()
    a.close(pos)

    assert balance_init - loss < a.balance
    assert a.year_tax < paid_tax


@pytest.mark.parametrize("amount", [-50, 50])
def test_loss_no_compensation(amount, price_data):
    balance_init = 5000
    a = SimAccount(price_data, balance=balance_init, steps_per_day=100)
    pos = a.open(amount)

    price_data.change_price(- amount // 10)
    loss = -pos.profit()
    a.close(pos)

    assert balance_init - loss == a.balance
    assert a.year_tax == 0