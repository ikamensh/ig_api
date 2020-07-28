from typing import ClassVar

from datasets.fade_over import fadeover_4_years
from env.sim.account import SimAccount
from env.sim.market_data import SimMarket
from robotrader.robotrader import RoboTrader
from loguru import logger


def simulate(rt_cls: ClassVar[RoboTrader], dataset=None, **kwargs):
    START_BALANCE = 5000

    price_dataset = dataset or fadeover_4_years()
    market_data = SimMarket(market_id="vix")
    account = SimAccount(balance=START_BALANCE, market_data=market_data,
                         steps_per_day=price_dataset.steps_per_day)
    rt = rt_cls(account, market_data, price_dataset.steps_per_day, **kwargs)

    for i, (low, high, delta) in enumerate(price_dataset):
        market_data.set_prices(low=low, high=high, delta=delta)
        account.step()
        rt.step()
        logger.info(
            f"Step {i} - Price {market_data.bid:.2f} / {market_data.ask:.2f}, Account: "
            f"{rt.account.balance + rt.account.profit():.2f} {len(rt.account.positions)}",
        )

    for p in list(rt.account.positions):
        rt.account.close(p)

    # visualize(rt)

    return (rt.account.balance - START_BALANCE) / START_BALANCE
