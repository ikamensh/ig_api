from robotrader.traders.evopot import EvoPotTrader
import markets


def test_evopot_init():
    trader = EvoPotTrader(None, markets.vix.code, 1, params = EvoPotTrader.random_params())