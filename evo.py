import collections
import random
from typing import List
from unittest.mock import Mock
import loguru
from blackopt.util.document import generate_report

loguru.logger = Mock()


from blackopt.abc import Problem, Solution
from blackopt.algorithms import RandomSearch, Gaos
import blackopt

from datasets.fade_over import fadeover_4_years, fadeover_1_year
from robotrader.traders.evo_trader import EvoTrader
from simulate import simulate



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
        params = EvoTrader.random_params()
        return VixTradingSolution(params)

    def mutate(self, rate: float) -> 'VixTradingSolution':
        rate = rate / len(self.params)
        new_params = []
        for p in self.params:
            if random.random() < rate:
                new_params.append(p * ( (3 / 4) + (1 / 4 + 1 / 3) * random.random()) )
            else:
                new_params.append(p)

        return VixTradingSolution(new_params)

def mapping(tpl):
    EvoTrader, ds, param = tpl
    return simulate(EvoTrader, ds, params = param)

class VixTradingProblem(Problem):

    def __str__(self):
        return f"{self.__class__.__name__}_{hash(self)}"

    def evaluate(self, s: VixTradingSolution) -> float:
        self.eval_count += 1
        n_tries = len(self.datasets)
        # datasets = random.sample(self.datasets, n_tries)
        self.datasets.append(fadeover_4_years())

        to_map = [(EvoTrader, ds, tuple(s.params)) for ds in self.datasets]
        changes = self.pool.map(mapping, to_map)

        # changes = []
        # for i, ds in enumerate(datasets):
        #     print(i)
        #     changes.append(simulate(EvoTrader, ds, params = s.params))

        changes = [-(abs(c) ** 2) * 100 if c < 0 else c for c in changes]
        median = changes[n_tries // 2]
        print(self.eval_count, median)
        avg = sum(changes) / n_tries

        return median + avg

    def __init__(self):
        self.datasets = collections.deque([fadeover_4_years() for i in range(50)], maxlen=50)
        import multiprocessing
        self.pool = multiprocessing.Pool()

def main(number):
    p = VixTradingProblem()
    solver = Gaos(p, VixTradingSolution, popsize=30, mutation_rate=1.2, equal_chances=0.01)
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
    main(20_000)

    print(f"{time.time() - t:.2f}")
