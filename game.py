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

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    t = time.time()

    n_tries = 1000
    runs = list(range(1000))

    import multiprocessing

    pool = multiprocessing.Pool()
    changes = pool.map(one_run, runs)

    plt.hist(changes, bins=200)
    print(sorted(changes))
    print(changes[500])
    print(f"{time.time() - t:.2f}")
    plt.show()

