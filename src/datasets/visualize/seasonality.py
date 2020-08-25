from collections import defaultdict
import datetime

from pennpaper import Metric, plot

import markets
from datasets.market_history import MarketHistory
from datasets.resolutions import Resolutions

def total_seconds(t: datetime.time):
    result = 0
    result += t.second
    result += 60 * t.minute
    result += 3600 * t.hour
    return result

def seasonality( ds: MarketHistory):

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



ds = MarketHistory.from_csv(markets.vix, Resolutions.MINUTE_30)
seasonality(ds)