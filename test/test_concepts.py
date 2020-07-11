import pytest

from robotrader.traders.random import RandomTrader

@pytest.mark.slow()
def test_trading_is_hard():
    from simulate import simulate

    changes = []
    for i in range(100):
        change, log = simulate(RandomTrader)
        changes.append(change)
        print(i)

    assert sum(changes) < 0