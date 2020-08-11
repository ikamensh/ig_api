from datetime import timedelta

from api.sim.sim_session import SimServer
from datasets.historical import ig_vix, ig_vix_eu
import markets

def test_start_time():
    """Both markets have valid data at start time. """

    s = SimServer(balance=5000, history=[ig_vix_eu, ig_vix])
    assert s.cur_time == max(ig_vix_eu.start, ig_vix.start)
    assert s.market_data[markets.vix.code].bid < s.market_data[markets.vix.code].ask
    assert s.market_data[markets.vix_eu.code].delta > 0


def test_data_changes(server):
    """Server changes price data with time. """

    md = server.market_data[markets.vix.code]
    vix_prices = md.bid, md.ask, md.delta
    time = md.time

    server.cur_time += timedelta(days=30)
    server.step()

    md = server.market_data[markets.vix.code]
    vix_prices_new = md.bid, md.ask, md.delta
    assert vix_prices != vix_prices_new

    assert md.time > time

