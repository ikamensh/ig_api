from typing import Dict

from datasets.price_dataset import PriceDataset
from env.sim.market_data import SimMarket
from robotrader.features.features import Feature


def vis_features(features: Dict[str, Feature], ds: PriceDataset):

    values = {k : [] for k in features}
    market_data = SimMarket(ds, ds.delta)

    for _, low, high in ds:
        market_data.set_prices(low, high)
        for k, f in features.items():
            f.update(market_data)
            values[k].append(f.value)


