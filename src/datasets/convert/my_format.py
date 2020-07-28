from datasets.market_history import MarketHistory
import markets
import datetime

def cboe_value(s):
    _open, high, low, _close = s
    low, high = float(low), float(high)
    if low > 25:
        delta = 0.2
    else:
        delta = 0.1
    return low, high, delta

import csv


def iter_my_format(rows):
    for d, low_bid, low_ask, high_bid, high_ask in rows:
        low_bid, low_ask, high_bid, high_ask = [
            float(x) for x in [low_bid, low_ask, high_bid, high_ask]
        ]
        delta = low_ask - low_bid
        assert delta > 0
        yield d, (low_bid + low_ask) / 2, (high_bid + high_ask) / 2, delta

to_convert = [markets.vix, markets.vix_eu, markets.us500]

for m in to_convert:

    md = MarketHistory(m)

    with open(md.csv_path) as f:
        r = csv.reader(f)
        rows = list(r)

        for t, low, high, delta in iter_my_format(rows):
            d = datetime.datetime.fromisoformat(t)
            md.add_record(date_time=d, low=low, high=high, delta=delta)

        md.compute_start_end_step()

    md.to_csv()