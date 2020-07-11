import os

from robotrader.traders.mov_avg import MovingAvgTrader
from robotrader.traders.random import RandomTrader
from simulate import simulate
from matplotlib import pyplot as plt

os.makedirs("logs", exist_ok=True)

changes = []
for i in range(100):
    change, log = simulate(RandomTrader, log=[])
    path = f"logs/game_{i}.log"
    with open(path, 'w') as f:
        print(os.path.abspath(path))
        f.write(str(change) + '\n')
        for line in log:
            f.write(line + '\n')

    changes.append(change)
    print(i)

plt.hist(changes, bins=100)
print(sorted(changes))
plt.show()
