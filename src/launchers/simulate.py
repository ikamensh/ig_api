import collections
from typing import ClassVar

from datasets.fade_over import fadeover_4_years
from datasets.market_history import MarketHistory
from api.sim.sim_session import SimulatedServer, SimSession
from robotrader.features.features import price
from robotrader.robotrader import RoboTrader
from loguru import logger

from robotrader.traders.exp_avg import ExpAvgTrader


def _visualize(features):
    from bokeh.plotting import figure, show
    from bokeh.colors.util import NamedColor
    from bokeh.layouts import column



    x = list(range(len(next(iter(features.values())))))

    price_fig = figure(title="prices", x_axis_label='x', y_axis_label='y', width=2500, plot_height=300)
    vs = [(k, v) for k, v in features.items() if "price" in k]
    for i, (k, v) in enumerate(vs):
        price_fig.line(x, v, legend_label=k, line_width=1, color=NamedColor.__all__[i + 29])

    dev_fig = figure(title="deviations", x_axis_label='x', y_axis_label='y', width=2500, plot_height=200)
    vs = [(k, v) for k, v in features.items() if "dev" in k]
    for i, (k, v) in enumerate(vs):
        dev_fig.line(x, v, legend_label=k, line_width=1, color=NamedColor.__all__[i + 28])

    pos_fig = figure(title="positions", x_axis_label='x', y_axis_label='y', width=2500,
                     plot_height=200)
    pos_fig.line(x, features["position"], legend_label="position", line_width=1, color="red")

    pos_d_fig = figure(title="delta position", x_axis_label='x', y_axis_label='y', width=2500,
                     plot_height=200)
    pos_d_fig.line(x, features["pos_change"], legend_label="opened", line_width=1, color="blue")

    show(column(price_fig, dev_fig, pos_fig, pos_d_fig))

def _get_position(s: SimulatedServer) -> int:
    result = 0
    if s.account.assets():
        result += s.account.assets()[s.market_data.market_code]
    return result

def simulate(rt_cls: ClassVar[RoboTrader], dataset: MarketHistory=None, visualize=False, **kwargs):
    START_BALANCE = 5000
    dataset = dataset or fadeover_4_years()

    keys = list(dataset.keys())
    start_date = keys[len(keys) // 3]
    history = dataset.slice(end=start_date)
    future = dataset.slice(start=start_date)
    print(len(history), len(future))

    server = SimulatedServer(balance=START_BALANCE, history=future)
    sess = SimSession(server)

    rt: RoboTrader = rt_cls(sess, dataset.market, dataset.steps_per_day, **kwargs)
    rt.warm_up(history)

    values = collections.defaultdict(list)
    while server.cur_time < dataset.end:
        rt.step()
        server.step()
        logger.info(
            f"At {server.cur_time} - Price {server.market_data.bid:.2f} / {server.market_data.ask:.2f}, Account: "
            f"{server.account.balance + server.account.profit():.2f} {len(server.account.positions)}",
        )

        if visualize:
            values["price"].append(price(rt.market_data()))
            pos_list = values["position"]
            pos_list.append( _get_position(server) )
            if len(pos_list) > 1:
                values["pos_change"].append(pos_list[-1] - pos_list[-2])
            else:
                values["pos_change"].append(pos_list[-1])

            for k, f in rt.features.items():
                values[k].append(f.value)

    for p in list(server.account.positions):
        server.account.close(p)

    if visualize:
        _visualize(values)

    return (server.account.balance - START_BALANCE) / START_BALANCE

if __name__ == "__main__":
    logger.remove()
    logger.add("sim.log")
    simulate(ExpAvgTrader, visualize=True)
