import csv
from typing import Callable, List, Tuple

class PriceDataset:
    # date, low, high
    data: List[ Tuple[str, float, float, float] ]
    steps_per_day: int
    delta: float

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


class HistoricDataset(PriceDataset):
    def __init__(self, source, decoder: Callable, steps_per_day):
        self.steps_per_day = steps_per_day
        with open(source) as f:
            r = csv.reader(f)
            rows = [t for t in r]

        self.data = list( decoder(rows) )


class SyntheticDataset(PriceDataset):
    def __init__(self, steps_per_day):
        self.steps_per_day = steps_per_day
        self.ctr = 0
        self.data = []

    def add_record(self, low, high, delta):
        self.data.append( (f"{self.ctr}", low, high, delta) )
        self.ctr += 1








