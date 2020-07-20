from datasets.price_dataset import SyntheticDataset
from datasets.historical import cboe_vix

import random


def upsample(low, high, times):
    seen_low = False
    seen_high = False

    for sample in range(times - 1):
        if random.random() < 1 / times:
            low_s = low
            seen_low = True
        else:
            low_s = low + (high - low) * random.random()

        if random.random() < 1 / times:
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


def random_slice(years: float):

    l = len(cboe_vix)
    size = int(365 * 5 / 7 * years) * cboe_vix.steps_per_day

    start = random.randint(0, l - size)

    ds = SyntheticDataset(steps_per_day=4)
    rate = ds.steps_per_day

    for i in range(start, start + size):
        date, low, high, delta = cboe_vix.data[i]

        for low_sample, high_sample in upsample(
            low, high, rate
        ):
            ds.add_record(low_sample, high_sample, delta)

        if random.random() < 0.2:
            rate = rate - 1 + random.randint(0, 2)
            rate = max( rate, ds.steps_per_day - 1)
            rate = min( rate, ds.steps_per_day + 1)

    return ds


if __name__ == "__main__":
    ds = random_slice(years=3)
    print(len(ds) / (52.3 * (ds.steps_per_day*5) ) )

    from matplotlib import pyplot as plt
    prices = [sum(d[1:])/2 for d in ds]

    plt.plot(prices)
    plt.grid()
    plt.title("Prices")
    plt.show()

