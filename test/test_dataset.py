import markets
from datasets.market_history import MarketHistory
import datetime

def test_slice():
    md = MarketHistory(markets.vix)
    for day in range(1, 10):
        date = datetime.datetime(year=2010, month=1, day=day)
        md.add_record(date, 10, 20, 1)

    start = datetime.datetime(year=2010, month=1, day=5)
    s = md.slice(start=start)
    assert len(s) > 0
    assert len(md) > len(s)