import pytest

import markets


@pytest.mark.parametrize("amount", [-50, 50])
def test_profit(acc, amount, price_data):
    balance_init = acc.balance
    pos = acc.open(amount, markets.vix.code)
    assert acc.year_tax == 0

    price_data[markets.vix.code].change_price(amount//10)
    profit = pos.profit()
    acc.close(pos)

    assert balance_init + profit > balance_init
    assert acc.year_tax > 0


@pytest.mark.parametrize("amount", [-50, 50])
def test_loss_compensation(acc, amount, price_data):

    paid_tax = 1000
    balance_init = acc.balance
    acc.year_tax = paid_tax
    pos = acc.open(amount, markets.vix.code)

    price_data[markets.vix.code].change_price( - amount // 10)
    loss = -pos.profit()
    acc.close(pos)

    assert balance_init - loss < acc.balance
    assert acc.year_tax < paid_tax


@pytest.mark.parametrize("amount", [-50, 50])
def test_loss_no_compensation(acc, amount, price_data):
    balance_init = acc.balance
    pos = acc.open(amount, markets.vix.code)

    price_data[markets.vix.code].change_price(- amount // 10)
    loss = -pos.profit()
    acc.close(pos)

    assert balance_init - loss == acc.balance
    assert acc.year_tax == 0