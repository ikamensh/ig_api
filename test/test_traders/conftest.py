import pytest

from sim.sim_session import SimSession, SimulatedServer

from datasets.historical import ig_vix

@pytest.fixture()
def sim_session():

    s = SimulatedServer(balance=5000, history=ig_vix)
    sess = SimSession(s)

    yield sess