import random

from datasets.synthetic.random_slice import random_slice
from robotrader.traders.potential_trader import PotentialTrader
from launchers.simulate import simulate


class TestTrader(PotentialTrader):
    short_limit = 0.3
    long_limit = 0.3

    def risk_factor(self) -> float:
        return random.random()

    def potential(self) -> float:
        return 2 * random.random() - 1


def test_once():
    simulate(TestTrader, dataset=random_slice(years=0.05))