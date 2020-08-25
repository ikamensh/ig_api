""" Run simulation for many runs and show distribution of results as a histogram. """

import os
import time

from loguru import logger
from matplotlib import pyplot as plt

from launchers.simulate import simulate
from robotrader.traders.exp_avg import ExpAvgTrader
from robotrader.traders.max_short import MaxShortTrader
from robotrader.traders.random import RandomTrader
from robotrader.traders.smart_short import SmartShort


def _one_run(x):
    i, rt_cls = x
    _disable_logging()
    change = simulate(rt_cls)
    print(i, change)
    return change


def _setup_logging(i):
    log_format = "<level>{message: <75}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    logger.info(f"Starting run {i}")
    logger.remove()
    try:
        os.remove(f"logs/game_{i}.log")
    except:
        pass
    logger.add(f"logs/game_{i}.log", format=log_format)


def _display_histogram(changes, rt_cls):
    changes = [c for c in changes if c is not None]
    print(len(changes))
    n_tries = len(changes)
    changes.sort()
    plt.grid()
    plt.hist(changes, bins=200)
    print([f"{c:.4f}" for c in changes])
    print(f"Median: {changes[n_tries // 2]:.4%}")
    print(f"Average: {sum(changes) / n_tries:.4%}")
    print(f"Loosing money in {len([c for c in changes if c < 0]) / n_tries:.2%} cases.")
    plt.savefig(f"{rt_cls.__name__}_results.png")
    plt.show()


def _sim_x_times(n_tries, rt_cls):
    if n_tries > 50:  # run with multiprocessing
        args = [(i, rt_cls) for i in range(n_tries)]
        import multiprocessing
        pool = multiprocessing.Pool()
        changes = pool.map(_one_run, args)
    else:  # don't bother with multiprocessing - too few runs
        changes = [_one_run( (x, rt_cls) ) for x in range(n_tries)]
    return changes


def _disable_logging():
    # disable logging - too slow for running many simulations

    def void(*args, **kwargs):
        pass

    logger.info = void
    logger.debug = void


def distribution(rt_cls):
    _disable_logging()
    t = time.time()
    changes = _sim_x_times(1000, rt_cls)
    _display_histogram(changes, rt_cls)
    print(f"{time.time() - t:.2f}")


if __name__ == "__main__":
    distribution(RandomTrader)
    # distribution(ExpAvgTrader)
    # distribution(SmartShort)

