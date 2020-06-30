import csv

from src.robotrader.traders.mov_avg import MovingAvgTrader
from src.robotrader.traders.random import RandomTrader
from src.robotrader.account import Platform
from matplotlib import pyplot as plt


def iter_my_format(rows):
    for i, (d, low_bid, low_ask, high_bid, high_ask) in enumerate(rows):
        low_bid, low_ask, high_bid, high_ask = [
            float(x) for x in [low_bid, low_ask, high_bid, high_ask]
        ]
        yield i, (d, low_bid, low_ask, high_bid, high_ask)


def iter_cboe(rows):
    for i, (d, _open, high, low, _close) in enumerate(rows[1:]):
        low, high = float(low), float(high)
        low_bid, low_ask = low - 0.08, low + 0.08
        high_bid, high_ask = high - 0.08, high + 0.08
        yield i, (d, low_bid, low_ask, high_bid, high_ask)

source, decoder = "../../data/ig_vix.csv", iter_my_format
# source, decoder = "../../data/ig_vix_eu.csv", iter_my_format
# source, decoder = "../../data/vixcurrent.csv", iter_cboe

with open(source) as f:
    r = csv.reader(f)
    rows = [t for t in r]


def simulate():
    platform = Platform()
    rt = MovingAvgTrader(platform)
    rt.account.balance = 5_000

    for i, (d, low_bid, low_ask, high_bid, high_ask) in decoder(rows):
        platform.set_prices(
            low_bid=low_bid, low_ask=low_ask, high_bid=high_bid, high_ask=high_ask
        )
        rt.step()
        if not i % 10:
            print(
                i,
                d,
                f"  {platform.market_bid:.2f} {platform.market_ask:.2f}  ",
                f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
            )

    for p in list(rt.account.positions):
        rt.account.close(p)

    for k, v in rt.history.items():
        plt.plot(v)
        plt.grid()
        plt.title(k)
        plt.show(dpi=400)
        plt.clf()

    return (rt.account.balance - 5_000) / 5_000


print(simulate())
#
# changes = [simulate() for i in range(5)]
# print(sum(changes))
#
#
# plt.hist(changes)
# plt.show()
