import collections
from datetime import timedelta
from typing import ClassVar

from bokeh.colors.util import NamedColor
from bokeh.layouts import column
from bokeh.plotting import figure, show
from loguru import logger

import markets
from robotrader.traders.smart_short import SmartShort
from trading_api.sim.sim_session import SimSession, SimServer
from datasets.synthetic.fade_over import fadeover_4_years
from datasets.market_history import MarketHistory
from datasets.synthetic.random_slice import random_slice
from robotrader.features.features import price
from robotrader.robotrader import RoboTrader
from robotrader.traders.exp_avg import ExpAvgTrader


def _visualize(features):
    """Display grouped plots of price and features vs time. """

    x = list(range(len(next(iter(features.values())))))

    def plot_group(name: str):
        price_fig = figure(title=name, x_axis_label='x', y_axis_label='y', width=2500,
                           plot_height=300)
        vs = [(k, v) for k, v in features.items() if name in k]

        for i, (k, v) in enumerate(vs):
            del features[k]
            price_fig.line(x, v, legend_label=k, line_width=1, color=NamedColor.__all__[i + 29])
        return price_fig

    price_fig = plot_group("price")
    dev_fig = plot_group("dev")
    mom_fig = plot_group("momentum")
    deb_fig = plot_group("debug")
    pos_fig = plot_group("position")
    pos_d_fig = plot_group("pos_change")
    nw_fig = plot_group("net_worth")

    show(column(price_fig, nw_fig, pos_fig, deb_fig, dev_fig, mom_fig, pos_d_fig))


def _get_position(s: SimServer) -> int:
    """Find the total amount of .vix position held. """
    result = 0
    if s.account.assets():
        result += s.account.assets()[markets.vix.code]
    return result


def _get_net_worth(s: SimServer) -> float:
    return s.account.balance + s.account.profit()


def _record_vis_data(rt, server, values):
    values["price"].append(price(rt.market_data()))
    values["net_worth"].append(_get_net_worth(server))
    pos_list = values["position"]
    pos_list.append(_get_position(server))
    if len(pos_list) > 1:
        values["pos_change"].append(pos_list[-1] - pos_list[-2])
    else:
        values["pos_change"].append(pos_list[-1])
    for k, f in rt.features.items():
        values[k].append(f.value)
    for k, v in rt.debug_info().items():
        values[f"debug_{k}"].append(v)


def _make_sim_session(START_BALANCE, dataset):
    keys = list(dataset.keys())
    start_date = keys[len(keys) // 3]
    history = dataset.slice(end=start_date)
    future = dataset.slice(start=start_date)
    server = SimServer(balance=START_BALANCE, history=[future])
    sess = SimSession(server)
    return history, server, sess


def simulate(rt_cls: ClassVar[RoboTrader], dataset: MarketHistory = None, visualize=False,
             **kwargs) -> float:
    """Run a single simulation of how a trading bot would perform on given dataset.

    First third of the dataset is used as history to bring features to speed,
    the trading takes place in the remaining 2/3 of the dataset.
    """

    START_BALANCE = 5000
    dataset = dataset or fadeover_4_years()
    dataset.market = markets.vix

    history, server, sess = _make_sim_session(START_BALANCE, dataset)

    rt: RoboTrader = rt_cls(sess, dataset.market.code, dataset.steps_per_day, **kwargs)
    rt.warm_up(history)

    values = collections.defaultdict(list)
    timestep = timedelta(days=1).total_seconds()
    while server._cur_time < dataset.end:
        rt.step()
        acc = server.account
        logger.info(
            f"At {server._cur_time} - account: {acc.balance + acc.profit():.2f} {len(acc.positions)}",
        )
        server.step(timestep)

        if visualize:
            _record_vis_data(rt, server, values)

    for p in list(server.account.positions):
        server.account.close(p)

    if visualize:
        _visualize(values)

    return (server.account.balance - START_BALANCE) / START_BALANCE


if __name__ == "__main__":
    import os

    log_name = "logs/_sim.log"
    folder = os.path.dirname(__file__)

    try:
        os.remove(os.path.join(folder, log_name))
    except:
        pass

    logger.remove()
    logger.add(log_name)
    simulate(SmartShort, dataset=random_slice(2), visualize=True)
