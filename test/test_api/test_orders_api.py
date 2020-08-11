import pytest

import markets
from api.exceptions import MarketClosedException


def test_get_orders(sess):

    result = sess.get_orders()
    assert isinstance(result, list)

def test_count_grows(sess):
    orders_before = sess.get_orders()
    target_market = markets._VIX
    try:
        order = sess.create_order(10, market=target_market)
    except MarketClosedException:
        pass
    else:
        orders_after = sess.get_orders()

        assert len(orders_after) > len(orders_before)
        assert order in orders_after

@pytest.mark.parametrize("amount", [10, -10])
def test_create_order(sess, amount):

    target_market = markets._VIX
    market_data = sess.get_market_data(target_market)
    target_level = market_data.bid - amount  # smaller price for long, bigger price for short
    order = sess.create_order(target_market, amount, level=target_level)
    assert order.amount == amount
    assert order.market_code == target_market
    assert order.deal_id


def test_close_order(sess):

    orders_before = sess.get_orders()
    target_market = markets._VIX
    market_data = sess.get_market_data(target_market)
    target_level = market_data.bid - amount  # smaller price for long, bigger price for short
    order = sess.create_order(target_market, amount, level=target_level)
    sess.delete_order(order)
    orders_after = sess.get_orders()
    assert len(orders_before) == len(orders_after)

def test_close_all(sess):

    orders = sess.get_orders()
    for o in orders:
        sess.delete_order(o)

    orders_after = sess.get_orders()

    assert not orders_after

