""" Run simulation for many runs and show distribution of results as a histogram. """

import os
import time

from loguru import logger
from matplotlib import pyplot as plt

from launchers.simulate import simulate
from robotrader.traders.exp_avg import ExpAvgTrader


def one_run(i):
    setup_logging(i)
    change = simulate(ExpAvgTrader)
    print(i, change)
    return change


def setup_logging(i):
    log_format = "<level>{message: <75}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    logger.info(f"Starting run {i}")
    logger.remove()
    try:
        os.remove(f"logs/game_{i}.log")
    except:
        pass
    logger.add(f"logs/game_{i}.log", format=log_format)


def display_histogram(changes):
    print(changes)
    # changes = [c for c in changes if c is not None]
    print(len(changes))
    n_tries = len(changes)
    changes.sort()
    plt.grid()
    print([f"{c:.4f}" for c in changes])
    plt.hist(changes, bins=200)
    print(f"Median: {changes[n_tries // 2]:.4%}")
    print(f"Average: {sum(changes) / n_tries:.4%}")
    print(f"Loosing money in {len([c for c in changes if c < 0]) / n_tries:.2%} cases.")
    plt.show()


def sim_x_times(n_tries):
    if n_tries > 50:  # run with multiprocessing
        runs = list(range(n_tries))
        import multiprocessing
        pool = multiprocessing.Pool()
        changes = pool.map(one_run, runs)
    else:  # don't bother with multiprocessing - too few runs
        changes = [one_run(i) for i in range(n_tries)]
    return changes


def disable_logging():
    # disable logging - too slow for running many simulations

    def void(*args, **kwargs):
        pass

    logger.info = void
    logger.debug = void


if __name__ == "__main__":
    disable_logging()

    t = time.time()

    changes = sim_x_times(100)
    display_histogram(changes)
    print(f"{time.time() - t:.2f}")
