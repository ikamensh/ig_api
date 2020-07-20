import datetime

from bokeh.plotting import figure, output_file, show

import markets
from api.data_model.market_history import MarketHistory

def cboe_date_parser(timestamp: str) -> datetime.datetime:
    month, day, year = timestamp.split('/')
    return datetime.datetime(day= int(day), month=int(month), year=int(year), hour=23, minute=59)

mh_ig = MarketHistory(markets.vix, resolution=None)
mh_official = MarketHistory(markets.vix_official, resolution=None, date_parser=cboe_date_parser)

def avg_price( strings ):
    return sum([float(s) for s in strings]) / len(strings)

cboe_slice = [(k,avg_price(v)) for k, v in mh_official.data.items() if mh_ig.start <= k <= mh_ig.end]
cboe_values = [e[1] for e in cboe_slice]

print("CBOE", cboe_slice[0][0], cboe_slice[-1][0])
print("IG", mh_ig.start, mh_ig.end)

ig_items = [ (k, avg_price(v)) for k, v in mh_ig.data.items()]
ig_compressed = []

ptr_ig = 0
temp = []
for k, v in cboe_slice:
    while ig_items[ptr_ig][0] < k and ptr_ig < len(ig_items):
        temp.append(ig_items[ptr_ig][1])
        ptr_ig += 1

    if temp:
        ig_compressed.append( avg_price(temp) )
        temp = []

print(len(mh_ig.data))
print(len(cboe_slice))
print(len(ig_compressed))

x = list(range(len(cboe_slice)))

# output_file("lines.html")
p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')

p.line(x, ig_compressed, legend_label="ig_compressed", line_width=1, color="red")
p.line(x, cboe_values, legend_label="cboe_values", line_width=1, color="green")

# show the results
show(p)