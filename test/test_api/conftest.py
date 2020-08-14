from datetime import datetime

import pytest

from trading_api.ig.ig_session import IgSession
from trading_api.sim.sim_session import SimServer, SimSession
from datasets.historical import ig_vix_eu, ig_vix

demo_account_id = "ikamen_demo"
demo_key = "ab3e4a55c5f40b911bbf045d43846f7ba70103bc"
demo_password = "BoringPassword123"

_sess = None

def real_session():
    global _sess
    if _sess is None:
        _sess = IgSession(demo_account_id, demo_key, demo_password)
    return _sess

def sim_session():
    server = SimServer(balance=5000, history=[ig_vix_eu, ig_vix])
    server._cur_time = datetime.now()
    s = SimSession(server)
    return s

@pytest.fixture(params=[real_session, sim_session])
def sess(request):
    factory = request.param
    yield factory()

@pytest.fixture()
def ig_session():
    yield real_session()
