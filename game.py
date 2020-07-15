import os

from robotrader.traders.exp_avg import ExpAvgTrader
from simulate import simulate
from matplotlib import pyplot as plt
import time
from loguru import logger

log_format = "<level>{message: <75}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"

def one_run(i):
    logger.info(f"Starting run {i}")
    logger.remove()
    try:
        os.remove(f"logs/game_{i}.log")
    except:
        pass
    logger.add(f"logs/game_{i}.log", format=log_format)
    change = simulate(ExpAvgTrader)
    return change

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    t = time.time()

    n_tries = 2
    if n_tries > 50:
        runs = list(range(n_tries))
        import multiprocessing
        pool = multiprocessing.Pool()
        changes = pool.map(one_run, runs)
    else:
        changes = [one_run(i) for i in range(n_tries)]
    changes.sort()

    plt.hist(changes, bins=200)
    print(f"Median: {changes[n_tries//2]:.4%}")
    print(f"Average: {sum(changes)/n_tries:.4%}")
    print(f"Loosing money in {len([c for c in changes if c < 0])/n_tries:.2%} cases.")
    print(f"{time.time() - t:.2f}")
    plt.show()

