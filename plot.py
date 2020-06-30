import csv

with open("data/ig_us500.csv") as f:
    r = csv.reader(f)
    rows = [t for t in r]

bids = [float(r[1]) for r in rows]
asks = [float(r[2]) for r in rows]


from matplotlib import pyplot as plt

plt.plot(bids)
plt.show()