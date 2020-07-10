from datasets.price_dataset import HistoricDataset
from config import data_folder

def iter_my_format(rows):
    for i, (d, low_bid, low_ask, high_bid, high_ask) in enumerate(rows):
        low_bid, low_ask, high_bid, high_ask = [
            float(x) for x in [low_bid, low_ask, high_bid, high_ask]
        ]
        yield d, (low_bid+ low_ask)/ 2, (high_bid + high_ask) / 2


def iter_cboe(rows):
    for i, (d, _open, high, low, _close) in enumerate(rows[1:]):
        low, high = float(low), float(high)
        yield d, low, high



ig_vix = HistoricDataset( data_folder + "/ig_vix.csv", iter_my_format, 4, delta=0.16)
ig_vix_eu = HistoricDataset( data_folder + "/ig_vix_eu.csv", iter_my_format, 4, delta=0.3)
cboe_vix = HistoricDataset( data_folder + "/vix_official.csv", iter_cboe, 1, delta=0.2)

