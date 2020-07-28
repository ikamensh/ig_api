from datasets.market_history import MarketHistory
from markets import vix_official
import datetime

def cboe_value(s):
    _open, high, low, _close = s
    low, high = float(low), float(high)
    if low > 25:
        delta = 0.2
    else:
        delta = 0.1
    return low, high, delta

from config import data_folder
import os
import csv

path = os.path.join(data_folder, "vix_original.csv")

md = MarketHistory(vix_official)

with open(path) as f:
    r = csv.reader(f)
    next(r)
    for t in r:
        timestamp, data = t[0], t[1:]
        open, high, low, close = [float(x) for x in data]
        delta = 0.1 if (high + low) / 2 < 25 else 0.2
        month, day, year = timestamp.split('/')
        month, day, year = [int(x) for x in [month, day, year]]
        d = datetime.datetime(year=year, month=month, day=day, hour=23, minute=59)
        md.add_record(date_time=d, low=low, high=high, delta=delta)

    md.compute_start_end_step()

md.to_csv()