from src.robotrader.traders.mov_avg import MovingAvgTrader
from env.price_data import PriceData
from matplotlib import pyplot as plt

# from datasets.historical import ig_vix as price_dataset
from datasets.random_slice import random_slice

def simulate():
    log = []
    price_dataset = random_slice(3)
    platform = PriceData(delta=price_dataset.delta)
    rt = MovingAvgTrader(platform, 5_000, price_dataset.steps_per_day, log)

    for i, (date, low, high) in enumerate(price_dataset):
        platform.set_prices(low=low, high=high)
        rt.step()
        log.append(
                f"{i} {platform.market_bid:.2f} {platform.market_ask:.2f}  "
                f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
            )

    for p in list(rt.account.positions):
        rt.account.close(p)

    # visualize(rt)

    return (rt.account.balance - 5_000) / 5_000, log


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
    change, log = simulate()
    if change < -1:
        with open("src/robotrader/game.log", 'w') as f:

            f.write(str(change) + '\n')
            for line in log:
                f.write(line + '\n')

        break
    changes.append(change)
    print(i)

plt.hist(changes, bins=100)
print(sorted(changes))
plt.show()
