from collections import defaultdict
import datetime

from pennpaper import Metric, plot

import markets
from datasets.market_history import MarketHistory
from datasets.resolutions import Resolutions

def total_seconds(t: datetime.datetime):
    result = 0
    result += t.second
    result += 60 * t.minute
    result += 3600 * t.hour
    result += 86400 * t.day
    return result

def daytime_trends(ds: MarketHistory):

    m = Metric(name="Price", x_label="time")

    low, high, delta = ds[ds.start]
    day_price = (low + high) / 2
    day = ds.start.date()

    for dt, (low, high, delta) in ds.items():
        if day != dt.date():
            day = dt.date()
            day_price = (low + high) / 2

        price = (low + high) / 2 - day_price
        time = dt.time()
        m.add_record(total_seconds(time), price)

    plot(m)


def monthly_trends(ds: MarketHistory):

    m = Metric(name="Price", x_label="time")

    low, high, delta = ds[ds.start]
    last = (low + high) / 2
    month = ds.start.date().month
    year = ds.start.date().year

    for dt, (low, high, delta) in ds.items():
        if month != dt.date().month:
            month = dt.date().month
            year = dt.date().year

        price = (low + high) / 2 - last
        last = (low + high) / 2
        time = dt - datetime.datetime(month=month, year=year, day=1)
        x = time.total_seconds()
        m.add_record(x, price)

    plot(m)


ds = MarketHistory.from_csv(markets.vix, Resolutions.MINUTE_30)
monthly_trends(ds)