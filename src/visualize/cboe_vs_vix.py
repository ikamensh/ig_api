import datetime
from typing import Dict, Tuple, List

import markets
from datasets.market_history import MarketHistory


def plot():
    ig_history = MarketHistory.from_csv(markets.vix)
    cboe_history = MarketHistory.from_csv(markets.cboe_vix)
    cboe_history = cboe_history.slice(start=ig_history.start, end=ig_history.end)

    print("CBOE", cboe_history.start, cboe_history.end)
    print("IG", ig_history.start, ig_history.end)

    ig_compressed = match(ig_history, cboe_history)
    ig_compressed = [(low + high) / 2 for low, high, delta in ig_compressed]
    cboe_values = [(low + high) / 2 for low, high, delta in cboe_history]


    print(len(ig_history))
    print(len(cboe_values))
    print(len(ig_compressed))

    x = list(range(len(cboe_values)))

    # output_file("lines.html")
    from bokeh.plotting import figure, show

    p = figure(
        title="simple line example", x_axis_label="x", y_axis_label="y", width=1500
    )

    p.line(x, ig_compressed, legend_label="ig_compressed", line_width=1, color="red")
    p.line(x, cboe_values, legend_label="cboe_values", line_width=1, color="green")

    show(p)


def match(source: MarketHistory, target: MarketHistory) -> MarketHistory:

    result = MarketHistory(source.market)
    items = list(source._data.items())

    temp = []
    ptr_ig = 0

    def compressed(lst: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
        lows = [t[0] for t in lst]
        highs = [t[0] for t in lst]
        deltas = [t[0] for t in lst]
        return min(lows), max(highs), sum(deltas) / len(deltas)

    for k in target._data:
        while items[ptr_ig][0] < k and ptr_ig < len(items):
            temp.append(items[ptr_ig][1])
            ptr_ig += 1

        if temp:
            result.add_record(k, *compressed(temp))
            temp = []
    return result


if __name__ == "__main__":
    plot()
