import pytest

from ig_api import markets
from ig_api.exceptions import MarketClosedException


def test_get_positions(sess):

    result = sess.get_positions()
    assert isinstance(result, list)

def test_count_grows(sess):
    positions_before = sess.get_positions()
    target_market = markets._VIX
    try:
        pos = sess.open_position(market=target_market, amount=10)
    except MarketClosedException:
        pass
    else:
        positions_after = sess.get_positions()

        assert len(positions_after) > len(positions_before)
        assert pos in positions_after

@pytest.mark.parametrize("amount", [10, -10])
def test_open_position(sess, amount):

    target_market = markets._VIX
    try:
        pos = sess.open_position(target_market, amount)
    except MarketClosedException:
        pass
    else:
        assert pos.amount == amount
        assert pos.market_data.market_code == target_market


def test_close_position(sess):

    positions_before = sess.get_positions()
    target_market = markets._VIX
    try:
        pos = sess.open_position(amount=10, market=target_market)
    except MarketClosedException:
        pass
    else:
        sess.close_position(pos)
        positions_after = sess.get_positions()
        assert len(positions_before) == len(positions_after)

def test_close_all(sess):

    positions_before = sess.get_positions()
    for pos in positions_before:
        sess.close_position(pos)

    positions_after = sess.get_positions()

    assert not positions_after

