from datetime import datetime

import pytest

from ig_api.ig_session import IgSession
from ig_api.sim.sim_session import SimServer, SimSession
from ig_api.datasets.historical import ig_vix_eu, ig_vix

demo_account_id = "ikamen_demo"
_keys = [
    "ab3e4a55c5f40b911bbf045d43846f7ba70103bc",
    "2f1f3c536e2ca6db2633284fe22f4ba2a60a3322",
    "e40a5b5f4b47ed7c9edc3c805a5ae0e28901426b",
]

def gen_keys():
    yield from _keys

demo_password = "BoringPassword123"

_sess = None

def real_session():
    global _sess
    if _sess is None:
        _sess = IgSession(demo_account_id, gen_keys(), demo_password)
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
