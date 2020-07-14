import markets
from env.real.market_data import RealMarket


def test_gets_data(sess):
    real_market = sess._get_market_data(markets.VIX)
    assert isinstance(real_market, RealMarket)
