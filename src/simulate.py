from typing import ClassVar

from datasets.fade_over import fadeover_4_years
from env.sim.account import SimAccount
from env.sim.market_data import SimMarket
from robotrader.robotrader import RoboTrader


def warm_up(robotrader: RoboTrader, ds):
    old = robotrader._warm_up
    robotrader._warm_up = True
    for _, low, high in ds:
        robotrader.market_data.set_prices(low, high)
        robotrader.step()
    robotrader._warm_up = old


def simulate(rt_cls: ClassVar[RoboTrader], log=None):
    START_BALANCE = 5000

    price_dataset = fadeover_4_years()
    market_data = SimMarket(delta=price_dataset.delta, market_id="vix")
    account = SimAccount(balance=START_BALANCE, market_data=market_data, steps_per_day=price_dataset.steps_per_day)
    rt = rt_cls(account, market_data)

    for i, (date, low, high) in enumerate(price_dataset):
        market_data.set_prices(low=low, high=high)
        rt.step()
        if log is not None:
            log.append(
                f"{i} {market_data.bid:.2f} {market_data.ask:.2f}  "
                f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
            )

    for p in list(rt.account.positions):
        rt.account.close(p)

    # visualize(rt)

    return (rt.account.balance - START_BALANCE) / START_BALANCE, log
