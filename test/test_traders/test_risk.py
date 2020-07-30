import pytest

import pytest

from robotrader.robotrader import RoboTrader

@pytest.mark.parametrize("amount", [-50, 50])
def test_positive_risk(amount, sim_session):
    market = sim_session._server.market_data.market_id
    rt = RoboTrader(sess=sim_session, target_market=market)
    rt.open(amount)
    assert rt._risk() > 0


@pytest.mark.parametrize("amount", [-50, 50])
def test_risk_proportional(amount, sim_session):
    market = sim_session._server.market_data.market_id
    rt = RoboTrader(sess=sim_session, target_market=market)
    pos1 = rt.open(amount)
    pos2 = rt.open(amount * 2)
    assert rt._pos_risk(pos1) < rt._pos_risk(pos2)


@pytest.mark.parametrize("amount", [-50, 50])
def test_risk_smaller_for_good_price(amount, sim_session):
    market = sim_session._server.market_data.market_id
    rt = RoboTrader(sess=sim_session, target_market=market)
    price_data = rt.market_data()
    price_data.set_prices(low=10, high=12, delta=1)
    pos1 = rt.open(amount)

    d_price = amount / 10
    # price changes in unfavorable direction
    price_data.set_prices(low=10 + d_price, high=12 + d_price, delta=1)
    pos2 = rt.open(amount)
    assert rt._pos_risk(pos1) < rt._pos_risk(pos2)
