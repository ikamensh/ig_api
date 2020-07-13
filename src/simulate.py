from typing import ClassVar

from datasets.random_slice import random_slice
from datasets.fade_over import fadeover_4_years
from env.price_data import PriceData
from robotrader.robotrader import RoboTrader


def warm_up(robotrader: RoboTrader, ds):
    old = robotrader.warm_up
    robotrader.warm_up = True
    for _, low, high in ds:
        robotrader.price_data.set_prices(low, high)
        robotrader.step()
    robotrader.warm_up = old


def simulate(rt_cls: ClassVar[RoboTrader], log=None):
    START_BALANCE = 5000

    price_dataset = fadeover_4_years()
    price_data = PriceData(delta=price_dataset.delta, market_id="vix")
    rt = rt_cls(price_data, START_BALANCE, price_dataset.steps_per_day, log)

    for i, (date, low, high) in enumerate(price_dataset):
        price_data.set_prices(low=low, high=high)
        rt.step()
        if log is not None:
            log.append(
                f"{i} {price_data.market_bid:.2f} {price_data.market_ask:.2f}  "
                f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
            )

    for p in list(rt.account.positions):
        rt.account.close(p)

    # visualize(rt)

    return (rt.account.balance - START_BALANCE) / START_BALANCE, log
