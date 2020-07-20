from datasets.price_dataset import HistoricDataset
from config import data_folder

def iter_my_format(rows):
    for d, low_bid, low_ask, high_bid, high_ask in rows:
        low_bid, low_ask, high_bid, high_ask = [
            float(x) for x in [low_bid, low_ask, high_bid, high_ask]
        ]
        delta = low_ask - low_bid
        assert delta > 0
        yield d, (low_bid + low_ask)/ 2, (high_bid + high_ask) / 2, delta


def iter_cboe(rows):
    for d, _open, high, low, _close in rows[1:]:
        low, high = float(low), float(high)
        if low > 25:
            delta = 0.2
        else:
            delta = 0.1
        yield d, low, high, delta


def get_ig_vix_ds():
    return HistoricDataset( data_folder + "/vix.csv", iter_my_format, steps_per_day=9)

def get_ig_vix_eu_ds():
    return HistoricDataset( data_folder + "/vix_eu.csv", iter_my_format, steps_per_day=8)

cboe_vix = HistoricDataset( data_folder + "/vix_official.csv", iter_cboe, 1)

