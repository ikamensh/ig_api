import datetime

import pytest

from api.sim._sim_account import SimAccount


@pytest.fixture()
def acc(price_data):
    yield SimAccount(price_data, balance=5000, start_date=datetime.datetime(year=1970, month=1, day=1))