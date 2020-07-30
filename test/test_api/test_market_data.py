import markets
from api.data_model.market_data import MarketData


def test_gets_data(sess):
    real_market = sess._get_market_data(markets._VIX)
    assert isinstance(real_market, MarketData)
