import pytest

import markets
from datasets.market_history import MarketHistory
from datasets.resolutions import Resolutions
import datetime


@pytest.fixture()
def vix_data():
    md = MarketHistory.from_csv(markets.vix, Resolutions.HOUR_2)
    yield md

def test_slice():
    md = MarketHistory(markets.vix)
    for day in range(1, 10):
        date = datetime.datetime(year=2010, month=1, day=day)
        md.add_record(date, 10, 20, 1)

    start = datetime.datetime(year=2010, month=1, day=5)
    s = md.slice(start=start)
    assert len(s) > 0
    assert len(md) > len(s)

def test_interpolates(vix_data):

    date = vix_data.start + (vix_data.end - vix_data.start) / 2
    assert isinstance(vix_data[date], tuple)


def test_unknown(vix_data):
    date = vix_data.start - datetime.timedelta(days=1)
    with pytest.raises(KeyError):
        val = vix_data[date]

def test_future(vix_data):
    date = vix_data.end + datetime.timedelta(days=1)
    assert vix_data[date] == vix_data[vix_data.end]



