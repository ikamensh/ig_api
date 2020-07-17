from robotrader.traders.evopot import EvoPotTrader


def test_evopot_init():
    trader = EvoPotTrader(None, None, 1, params = EvoPotTrader.random_params())