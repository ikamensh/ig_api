from typing import ClassVar

from datasets.fade_over import fadeover_4_years
from datasets.market_history import MarketHistory
from sim.sim_session import SimulatedServer, SimSession
from robotrader.robotrader import RoboTrader
from loguru import logger


def simulate(rt_cls: ClassVar[RoboTrader], dataset: MarketHistory=None, **kwargs):
    START_BALANCE = 5000
    dataset = dataset or fadeover_4_years()

    server = SimulatedServer(balance=START_BALANCE, history=dataset)
    sess = SimSession(server)

    rt = rt_cls(sess, dataset.market, dataset.steps_per_day, **kwargs)

    while server.cur_time < dataset.end:
        rt.step()
        server.step()
        logger.info(
            f"At {server.cur_time} - Price {server.market_data.bid:.2f} / {server.market_data.ask:.2f}, Account: "
            f"{server.account.balance + server.account.profit():.2f} {len(server.account.positions)}",
        )

    for p in list(server.account.positions):
        server.account.close(p)

    # visualize(rt)

    return (server.account.balance - START_BALANCE) / START_BALANCE
