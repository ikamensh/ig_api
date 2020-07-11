from typing import ClassVar

from datasets.random_slice import random_slice
from env.price_data import PriceData
from robotrader.robotrader import RoboTrader

START_BALANCE = 5000

def simulate(rt_cls: ClassVar[RoboTrader], log = None):
    price_dataset = random_slice(3)
    platform = PriceData(delta=price_dataset.delta)
    rt = rt_cls(platform, START_BALANCE, price_dataset.steps_per_day, log)

    for i, (date, low, high) in enumerate(price_dataset):
        platform.set_prices(low=low, high=high)
        rt.step()
        if log is not None:
            log.append(
                    f"{i} {platform.market_bid:.2f} {platform.market_ask:.2f}  "
                    f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
                )

    for p in list(rt.account.positions):
        rt.account.close(p)

    # visualize(rt)

    return (rt.account.balance - START_BALANCE) / START_BALANCE, log