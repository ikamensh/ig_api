import typing
from datetime import datetime, timedelta
import random

from ig_api.datasets.market_history import MarketHistory
from ig_api.datasets.synthetic.random_slice import random_slice


def fade_over(seq: typing.List[MarketHistory], overlap = 0.15) -> MarketHistory:
    assert len(seq) > 1, "Seq must be a sequence of PriceDataset objects, optimally about a year lenght"


    cur = seq.pop()
    n = len(cur)
    cur_it = iter(cur)

    result = MarketHistory(cur.market)
    date_time = datetime(year=1970, month=1, day=1)

    def add_record(low, high, delta):
        nonlocal date_time
        result.add_record(date_time, low, high, delta)
        date_time += timedelta(days=1)


    while seq:
        nxt = seq.pop()
        nxt_it = iter(nxt)
        assert cur.steps_per_day == nxt.steps_per_day

        n_fadeover = int(n * overlap)
        n_pure = n - n_fadeover
        for i in range(n_pure):
            low, high, delta = next(cur_it)
            add_record(low, high, delta)

        for i in range(n_fadeover):
            low1, high1, d1 = next(cur_it)
            low2, high2, d2 = next(nxt_it)
            k = i / n_fadeover
            add_record(low1 * (1-k) + low2 * k, high1 * (1-k) + high2 * k, d1)

        n = len(nxt) - n_fadeover
        cur = nxt
        cur_it = nxt_it

    for low, high, delta in cur_it:
        add_record(low, high, delta)

    result.compute_start_end_step()
    result.steps_per_day = cur.steps_per_day

    return result


def fadeover_4_years():
    n_slices = random.randint(2, 4)
    slices = [random_slice(years=0.5 + 2 * random.random()) for i in range(n_slices)]
    return fade_over(slices)


def fadeover_1_year():
    slices = [random_slice(years=0.65) for i in range(2)]
    return fade_over(slices)


if __name__ == "__main__":

    ds = fadeover_4_years()
    ds.plot()

    print(ds.steps_per_day)
    print( len(ds) / (52.3 * (ds.steps_per_day * 5)) )