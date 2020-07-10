from src.robotrader.traders.mov_avg import MovingAvgTrader
from src.robotrader.traders.random import RandomTrader
from src.robotrader.account import Platform
from matplotlib import pyplot as plt

# from datasets.historical import ig_vix as price_dataset
from datasets.random_slice import random_slice


def simulate():
    price_dataset = random_slice(3)
    platform = Platform(delta=price_dataset.delta)
    rt = MovingAvgTrader(platform, 5_000, price_dataset.steps_per_day)

    for i, (date, low, high) in enumerate(price_dataset):
        platform.set_prices(low=low, high=high)
        rt.step()
        # if not i % 10:
        #     print(
        #         i,
        #         date,
        #         f"  {platform.market_bid:.2f} {platform.market_ask:.2f}  ",
        #         f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
        #     )

    for p in list(rt.account.positions):
        rt.account.close(p)

    # visualize(rt)

    return (rt.account.balance - 5_000) / 5_000


def visualize(rt):
    print(list(rt.history.keys()))
    prices = ["price_avg", "price_high", "price_low"]
    for k in prices:
        v = rt.history[k]
        plt.plot(v, linewidth=0.5)
    plt.grid()
    plt.title("Prices")
    plt.savefig("plots/prices.png", dpi=400)
    plt.clf()

    devs = ["day_dev", "week_dev", "neg_day_dev", "neg_week_dev", "delta"]

    for k in devs:
        v = rt.history[k]
        plt.plot(v, linewidth=0.5)
    plt.grid()
    plt.title("Devs")
    plt.savefig("plots/devs.png", dpi=400)
    plt.clf()

    for k in set(rt.history.keys()) - set(prices) - set(devs):
        v = rt.history[k]
        plt.plot(v, linewidth=0.5)
        plt.grid()
        plt.title(k)
        plt.savefig(f"plots/{k}.png", dpi=400)
        plt.clf()


changes = []
for i in range(100):
    changes.append(simulate())
    print(i)

plt.hist(changes)
plt.show()
