import typing
from datasets.price_dataset import PriceDataset, SyntheticDataset
from datasets.random_slice import random_slice


def fade_over(seq: typing.List[PriceDataset], overlap = 0.15) -> PriceDataset:
    assert len(seq) > 1, "Seq must be a sequence of PriceDataset objects, optimally about a year lenght"


    cur = seq.pop()
    n = len(cur)
    cur_it = iter(cur)

    result = SyntheticDataset(cur.steps_per_day, delta=cur.delta)

    while seq:
        nxt = seq.pop()
        nxt_it = iter(nxt)
        assert cur.steps_per_day == nxt.steps_per_day

        n_fadeover = int(n * overlap)
        n_pure = n - n_fadeover
        for i in range(n_pure):
            _, low, high = next(cur_it)
            result.add_record(low, high)
        for i in range(n_fadeover):
            _, low1, high1 = next(cur_it)
            _, low2, high2 = next(nxt_it)
            k = i / n_fadeover
            result.add_record(low1 * (1-k) + low2 * k, high1 * (1-k) + high2 * k)

        n = len(nxt) - n_fadeover
        cur = nxt
        cur_it = nxt_it

    for _, low, high in cur_it:
        result.add_record(low, high)

    return result


def fadeover_4_years():
    slices = [random_slice(years=1.5) for i in range(3)]
    return fade_over(slices)


if __name__ == "__main__":

    slices = [random_slice(years=1.5) for i in range(3)]
    ds = fade_over(slices)

    from matplotlib import pyplot as plt
    prices = [sum(d[1:])/2 for d in ds]

    plt.plot(prices)
    plt.grid()
    plt.title("Prices")
    plt.show()

    print(ds.steps_per_day)
    print( len(ds) / (52.3 * (ds.steps_per_day * 5)) )