import pytest

from trading_api.sim.sim_session import SimSession, SimServer

from datasets.historical import ig_vix

@pytest.fixture()
def sim_session():

    s = SimServer(balance=5000, history=[ig_vix])
    sess = SimSession(s)

    yield sess