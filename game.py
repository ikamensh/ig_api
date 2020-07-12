import os

from robotrader.traders.exp_avg import ExpAvgTrader
from robotrader.traders.momentum import MomentumTrader
from robotrader.traders.random import RandomTrader
from simulate import simulate
from matplotlib import pyplot as plt
import time


def one_run(i):
    change, log = simulate(ExpAvgTrader, log=None)
    path = f"logs/game_{i}.log"
    # with open(path, 'w') as f:
    #     print(os.path.abspath(path))
    #     f.write(str(change) + '\n')
    #     for line in log:
    #         f.write(line + '\n')

    print(i)
    return change

one_run(1)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    t = time.time()

    n_tries = 1000
    runs = list(range(n_tries))

    import multiprocessing

    pool = multiprocessing.Pool()
    changes = pool.map(one_run, runs)
    changes.sort()

    plt.hist(changes, bins=200)
    print(f"Median: {changes[n_tries//2]:.4%}")
    print(f"Average: {sum(changes)/n_tries:.4%}")
    print(f"Loosing money in {len([c for c in changes if c < 0])/n_tries:.2%} cases.")
    print(f"{time.time() - t:.2f}")
    plt.show()

