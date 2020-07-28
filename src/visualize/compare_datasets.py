import collections
import copy
from typing import Dict

from bokeh.colors.util import NamedColor
from bokeh.plotting import figure, show

import markets
from datasets.market_history import MarketHistory
from env.sim.market_data import SimMarket
from robotrader.features.features import Feature, price, ExpAvg, Momentum
from visualize.cboe_vs_vix import match


def vis_features(features: Dict[str, Feature], ds1: MarketHistory, ds2: MarketHistory):
    assert len(ds1) == len(ds2), f"{len(ds1)} != {len(ds2)}"

    fig = figure(title="simple line example", x_axis_label='x', y_axis_label='y', width=1500)

    vals_1 = _plot_features(ds1, features, fig, 1)
    vals_2 = _plot_features(ds2, features, fig, 2)

    show(fig)


    fig_ratios = figure(title="ratio", x_axis_label='x', y_axis_label='ratio', width=1500)

    x = list(range(len(next(iter(vals_1.values())))))
    for i, k in enumerate(features):
        ratio = [(v1 + 1e-10) / (v2 + 1e-10) for v1, v2 in zip(vals_1[k], vals_2[k])]
        fig_ratios.line(x, ratio, legend_label=f"{k}_ratio", line_width=1,
                 color=NamedColor.__all__[i * 10 + 10])

    show(fig_ratios)




def _plot_features(ds: MarketHistory, features, fig, suffix):
    features_2 = copy.deepcopy(features)
    values = collections.defaultdict(list)
    market_data = SimMarket("fake_market_id")
    for low, high, delta in ds:
        market_data.set_prices(low, high, delta)
        for k, f in features_2.items():
            f.update(market_data)
            values[k].append(f.value)
        values["price"].append(price(market_data))
    x = list(range(len(ds)))
    for i, (k, v) in enumerate(values.items()):
        fig.line(x, v, legend_label=f"{k}_{suffix}", line_width=1, color=NamedColor.__all__[i*10 + suffix + 10])

    return values


if __name__ == "__main__":
    ig_history = MarketHistory.from_csv(markets.vix)
    cboe_history = MarketHistory.from_csv(markets.cboe_vix)
    cboe_history = cboe_history.slice(start=ig_history.start, end=ig_history.end)

    ig_compressed = match(ig_history, cboe_history)

    def beta_days(days):
        return 1 - 0.6 / days

    feats = {
        # "daily_dev": expavg_stddev(window=1, smoothing=beta_days(30)),
        # "weekly_dev": expavg_stddev(window=5, smoothing=beta_days(30)),
        "exp_avg": ExpAvg(beta=beta_days(30), fn=price),
        "momentum": ExpAvg(beta=beta_days(30), fn=Momentum(price))
    }
    print(len(ig_compressed), len(cboe_history))
    vis_features(feats, cboe_history, ig_compressed)
