import datetime

import pytest

from api.sim._sim_account import SimAccount
from api.sim.sim_session import SimServer
from datasets.historical import ig_vix_eu, ig_vix


@pytest.fixture()
def acc(price_data):
    yield SimAccount(price_data, balance=5000, start_date=datetime.datetime(year=1970, month=1, day=1))


@pytest.fixture()
def server():
    s = SimServer(balance=5000, history=[ig_vix_eu, ig_vix])
    yield s