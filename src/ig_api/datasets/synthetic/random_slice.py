from datetime import datetime, timedelta
import random

from ig_api.datasets.historical import cboe_vix
from ig_api.datasets.market_history import MarketHistory


def upsample(low: float, high: float, k: int):
    """create k samples that lie between low and high values. """
    assert high >= low
    assert k > 0

    if k == 1:
        yield from [ (low, high) ]
        return

    seen_low = False
    seen_high = False

    for sample in range(k - 1):
        if random.random() < 1 / k:
            low_s = low
            seen_low = True
        else:
            low_s = low + (high - low) * random.random()

        if random.random() < 1 / k:
            high_s = high
            seen_high = True
        else:
            high_s = low_s + (high - low_s) * random.random()

        yield low_s, high_s

    if not seen_low:
        low_s = low
    else:
        low_s = low + (high - low) * random.random()

    if not seen_high:
        high_s = high
    else:
        high_s = low_s + (high - low_s) * random.random()
    yield low_s, high_s


def random_slice(years: float, source: MarketHistory = cboe_vix, resolution: int = 4):
    """ Take a random slice of a given dataset of given length.

    Adds random compression/dilation on time axis.

    Args:
        years: approx. length of the slice.
        source: dataset to take a slice from.
        resolution: how many steps per day of data to use.

    """
    l = len(source)
    size = int(365 * 5 / 7 * years) * source.steps_per_day

    start = random.randint(0, l - size)

    result = MarketHistory(market=source.market)
    rate = max(resolution // source.steps_per_day, 1)

    date_time = datetime(year=1970, month=1, day=1)

    seq = list(source)
    min_rate = max(1, resolution - 2)
    max_rate = resolution + 2

    for i in range(start, start + size):
        low, high, delta = seq[i]

        for low_sample, high_sample in upsample(low, high, rate):
            result.add_record(date_time, low_sample, high_sample, delta)
            date_time += timedelta(days=1)

        if random.random() < 0.2:
            rate = rate - 1 + random.randint(0, 2)
            rate = max(rate, min_rate)
            rate = min(rate, max_rate)

    result.compute_start_end_step()
    result.steps_per_day = resolution
    return result


if __name__ == "__main__":
    ds = random_slice(years=3)
    print(len(ds) / (52.3 * (ds.steps_per_day * 5)))
