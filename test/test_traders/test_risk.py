import pytest
import markets

from robotrader.robotrader import RoboTrader

@pytest.mark.parametrize("amount", [-50, 50])
def test_positive_risk(amount, sim_session):
    rt = RoboTrader(sess=sim_session, target_market=markets.vix.code)
    rt.open(amount)
    assert rt._risk() > 0


@pytest.mark.parametrize("amount", [-50, 50])
def test_risk_proportional(amount, sim_session):
    rt = RoboTrader(sess=sim_session, target_market=markets.vix.code)
    pos1 = rt.open(amount)
    pos2 = rt.open(amount * 2)
    assert rt._pos_risk(pos1) < rt._pos_risk(pos2)


@pytest.mark.parametrize("amount", [-50, 50])
def test_risk_smaller_for_good_price(amount, sim_session):
    rt = RoboTrader(sess=sim_session, target_market=markets.vix.code)
    price_data = sim_session._server.market_data[markets.vix.code]

    price_data.set_prices(low=10, high=12, delta=1)
    pos1 = rt.open(amount)

    d_price = amount / 10
    # price changes in unfavorable direction
    price_data.set_prices(low=10 + d_price, high=12 + d_price, delta=1)
    pos2 = rt.open(amount)
    assert rt._pos_risk(pos1) < rt._pos_risk(pos2)
