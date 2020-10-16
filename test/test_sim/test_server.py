from datetime import timedelta

from ig_api.sim.sim_session import SimServer
from ig_api.datasets.historical import ig_vix, ig_vix_eu
from ig_api import markets

def test_start_time():
    """Both markets have valid data at start time. """

    s = SimServer(balance=5000, history=[ig_vix_eu, ig_vix])
    assert s._cur_time == max(ig_vix_eu.start, ig_vix.start)
    assert s.market_data[markets.vix.code].bid < s.market_data[markets.vix.code].ask
    assert s.market_data[markets.vix_eu.code].delta > 0


def test_data_changes(server):
    """Server changes price data with time. """

    md = server.market_data[markets.vix.code]
    vix_prices = md.bid, md.ask, md.delta
    time = md.time

    server.step(timedelta(days=30).total_seconds())

    md = server.market_data[markets.vix.code]
    vix_prices_new = md.bid, md.ask, md.delta
    assert vix_prices != vix_prices_new

    assert md.time > time

