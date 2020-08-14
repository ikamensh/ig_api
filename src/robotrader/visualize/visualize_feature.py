import collections
from typing import Dict

from bokeh.colors.util import NamedColor
from bokeh.plotting import figure, show

from trading_api.sim._sim_market_data import SimMarket
from datasets.market_history import MarketHistory
from robotrader.features.features import Feature, price


def vis_features(features: Dict[str, Feature], ds: MarketHistory):

    values = collections.defaultdict(list)
    market_data = SimMarket("fake_market_id")

    for low, high, delta in ds:
        market_data.set_prices(low, high, delta)
        for k, f in features.items():
            f.update(market_data)
            values[k].append(f.value)
        values["price"].append(price(market_data))

    p = figure(title="simple line example", x_axis_label='x', y_axis_label='y', width=2000)

    x = list(range(len(ds)))
    for i, (k, v) in enumerate(values.items()):
        p.line(x, v, legend_label=k, line_width=1, color=NamedColor.__all__[i+10])

    show(p)


if __name__ == "__main__":
    params = [-11.155270207184385, 74, 0.3086474969688482, -0.21119218927625483, 76, 94,
              0.5563704862673999, -0.5189416318568625, 20, 208, 30, -0.0457313069459464,
              -4.366558211359452, 35.08424596762409, -4.333129088307059, 1.3519515204077648,
              -0.8847595303563158, 0.09072866090354159]

    from robotrader.traders.evopot import EvoPotTrader
    from datasets.historical import ig_vix

    tdr = EvoPotTrader(None, None, ig_vix.steps_per_day, params=params)
    vis_features(tdr.features, ig_vix)

