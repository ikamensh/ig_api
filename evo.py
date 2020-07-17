import collections
import random
from typing import List
from loguru import logger
from blackopt.util.document import generate_report

from blackopt.abc import Problem, Solution
from blackopt.algorithms import RandomSearch, Gaos

from datasets.fade_over import fadeover_4_years, fadeover_1_year
from robotrader.traders.evopot import EvoPotTrader
from simulate import simulate


def void(*args, **kwargs):
    pass

info = logger.info
logger.add("evo.log")
logger.info = void
logger.debug = void


class VixTradingSolution(Solution):

    def __init__(self, params):
        self.params: List[float] = params

    def crossover(self, other: 'VixTradingSolution') -> List['VixTradingSolution']:
        crossover_point = random.randint(0, len(self.params))
        parents = [self, other]
        random.shuffle(parents)
        a, b = parents
        new_params = a.params[:crossover_point] + b.params[crossover_point:]
        return [VixTradingSolution(new_params)]

    @staticmethod
    def random_solution() -> 'VixTradingSolution':
        params = EvoPotTrader.random_params()
        return VixTradingSolution(params)

    def mutate(self, rate: float) -> 'VixTradingSolution':
        rate = rate / len(self.params)
        new_params = []
        for p in self.params:
            if random.random() < rate:
                new = p * ((3 / 4) + (1 / 4 + 1 / 3) * random.random())
                if random.random() < 0.2:
                    new = -new
                new_params.append(new)
            else:
                new_params.append(p)

        return VixTradingSolution(new_params)


def mapping(tpl):
    EvoTrader, ds, param = tpl
    return simulate(EvoTrader, ds, params=param)


class VixTradingProblem(Problem):

    def __str__(self):
        return f"{self.__class__.__name__}_{hash(self)}"

    def evaluate(self, s: VixTradingSolution) -> float:

        # Idea: trials, try on 10 -> 100 -> 1000 datasets, try next only if excellent on prev.

        self.eval_count += 1
        n_tries = len(self.datasets)
        # datasets = random.sample(self.datasets, n_tries)
        self.datasets.append(fadeover_4_years())

        to_map = [(EvoPotTrader, ds, tuple(s.params)) for ds in self.datasets]
        changes = self.pool.map(mapping, to_map)

        # changes = []
        # for i, ds in enumerate(datasets):
        #     print(i)
        #     changes.append(simulate(EvoTrader, ds, params = s.params))
        changes.sort()
        median = changes[n_tries // 2]
        n_negative = len([c for c in changes if c <0])
        changes = [-(abs(c) ** 2) * 1000 if c < 0 else c for c in changes]
        avg = sum(changes) / n_tries
        info(f"{self.eval_count: >4}, {median: >6.2f}, {avg: >7.1f}, {n_negative: >2}, {s.params}")

        return median + avg

    def __init__(self):
        self.datasets = collections.deque([fadeover_4_years() for i in range(50)], maxlen=50)
        import multiprocessing
        self.pool = multiprocessing.Pool()


def main(number):
    p = VixTradingProblem()
    # solver = RandomSearch(p, VixTradingSolution)
    solver = Gaos(p, VixTradingSolution, popsize=30, mutation_rate=0.8, equal_chances=0.01)
    solver.solve(number)
    print(solver.best_solution.params)
    generate_report(p, {solver: solver.metrics})


if __name__ == "__main__":
    # from cProfile import Profile
    #
    # profiler = Profile()
    # profiler.runcall(main)
    # profiler.print_stats('cumulative')
    import time

    t = time.time()
    main(50_000)

    print(f"{time.time() - t:.2f}")
