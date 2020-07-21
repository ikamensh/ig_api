import collections
import copy
from typing import Dict

from bokeh.colors.util import NamedColor
from bokeh.plotting import figure, show

from datasets.price_dataset import PriceDataset
from env.sim.market_data import SimMarket
from robotrader.features.features import Feature, price


def vis_features(features: Dict[str, Feature], ds1: PriceDataset, ds2: PriceDataset):
    assert len(ds1) == len(ds2)

    fig = figure(title="simple line example", x_axis_label='x', y_axis_label='y', width=2000)

    _plot_features(ds1, features, fig, "_1")
    _plot_features(ds2, features, fig, "_2")

    show(fig)


def _plot_features(ds, features, fig, suffix):
    features_2 = copy.deepcopy(features)
    values = collections.defaultdict(list)
    market_data = SimMarket("fake_market_id")
    for _, low, high, delta in ds:
        market_data.set_prices(low, high, delta)
        for k, f in features_2.items():
            f.update(market_data)
            values[k].append(f.value)
        values["price"].append(price(market_data))
    x = list(range(len(ds)))
    for i, (k, v) in enumerate(values.items()):
        fig.line(x, v, legend_label=k + suffix, line_width=1, color=NamedColor.__all__[i + 10])


if __name__ == "__main__":
    pass
