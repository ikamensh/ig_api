import pytest
import sys
from loguru import logger

from robotrader.traders.random import RandomTrader

@pytest.mark.slow()
@pytest.mark.skip()
def test_trading_is_hard():
    from launchers.simulate import simulate
    logger.remove(0)

    changes = []
    for i in range(100):
        change = simulate(RandomTrader)
        changes.append(change)

    assert sum(changes) < 0
    logger.add(sys.stderr)