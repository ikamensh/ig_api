import markets


def test_get_positions(sess):

    result = sess.get_positions()
    assert isinstance(result, list)

def test_count_grows(sess):
    positions_before = sess.get_positions()
    target_market = markets.VIX
    pos = sess.open_position(10, market=target_market)
    positions_after = sess.get_positions()

    assert len(positions_after) > len(positions_before)
    assert pos in positions_after


def test_open_long_position(sess):

    target_market = markets.VIX
    pos = sess.open_position(10, market=target_market)
    assert pos.amount == 10
    assert pos.market_data.market_id == target_market

def test_open_short_position(sess):

    target_market = markets.VIX
    pos = sess.open_position(-10, market=target_market)
    assert pos.amount == -10
    assert pos.market_data.market_id == target_market


def test_close_position(sess):

    positions_before = sess.get_positions()
    target_market = markets.VIX
    pos = sess.open_position(10, market=target_market)
    sess.close_position(pos)
    positions_after = sess.get_positions()

    assert len(positions_before) == len(positions_after)

