import typing
from loguru import logger

from datasets.price_dataset import PriceDataset
from env.abc.account import Account
from env.abc.market_data import MarketData
from env.exceptions import CantOpenPosition
from env.sim.market_data import SimMarket

if typing.TYPE_CHECKING:
    from robotrader.features.features import Feature



class RoboTrader:
    def __init__(self, account: Account, market_data: MarketData, steps_per_day: int = None):
        self.account = account
        self.market_data = market_data
        self.features: typing.Dict[str, Feature] = {}


    def step(self):
        logger.debug(f"{self.__class__.__name__} is updating features.")
        for k, f in self.features.items():
            f.update(self.market_data)
            logger.debug(f"{k: <15} = {f.value:.3f}")
        try:
            self.decide_actions()
        except CantOpenPosition:
            pass

        self.account.step()


    def decide_actions(self):
        raise NotImplementedError

    def warm_up(self, ds: PriceDataset):
        logger.info(f"Running warmup on {ds}")
        logger.disable(__name__)
        old_market_data = self.market_data

        self.market_data = SimMarket(ds, ds.delta)

        for _, low, high in ds:
            self.market_data.set_prices(low, high)
            for k, f in self.features.items():
                f.update(self.market_data)

        self.market_data = old_market_data
        logger.enable(__name__)

        logger.debug(f"{self.__class__.__name__} updated features via warmup.")
        for k, f in self.features.items():
            logger.debug(f"{k: >15} = {f.value:.3f}")


    def max_long_amount(self):

        free_money = self.account.balance - self.account.risk()
        risk_per_unit = self.market_data.ask - self.market_data.lowest

        return free_money / risk_per_unit


    def max_short_amount(self):
        free_money = self.account.balance - self.account.risk()
        risk_per_unit = self.market_data.highest - self.market_data.bid

        return free_money / risk_per_unit