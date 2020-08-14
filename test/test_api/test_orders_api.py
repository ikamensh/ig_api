import pytest

import markets
from trading_api.data_model.order import Order
from trading_api.exceptions import MarketClosedException, OrderNotFoundError


def test_get_orders(sess):

    result = sess.get_orders()
    assert isinstance(result, list)

def test_count_grows(sess):
    orders_before = sess.get_orders()
    target_market = markets._VIX
    level = sess.get_market_data(target_market).ask - 1
    try:
        order = sess.create_order(amount=10, market=target_market, level=level)
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
    target_level = market_data.bid - 1  # smaller price for long, bigger price for short
    order = sess.create_order(target_market, 10, level=target_level)
    sess.delete_order(order)
    orders_after = sess.get_orders()
    assert len(orders_before) == len(orders_after)


def test_close_nonexistent(sess):

    target_market = markets._VIX
    order = Order(amount=10, level=150, market_code=target_market, deal_id="FAKE")
    with pytest.raises(OrderNotFoundError):
        sess.delete_order(order)




def test_close_all(sess):

    orders = sess.get_orders()
    for o in orders:
        sess.delete_order(o)
    import time
    time.sleep(0.3)
    orders_after = sess.get_orders()

    assert not orders_after

