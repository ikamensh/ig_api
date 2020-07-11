from matplotlib import pyplot as plt


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