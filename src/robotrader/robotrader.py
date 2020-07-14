import collections
import typing
from unittest.mock import Mock

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
        self.history = collections.defaultdict(list)
        self.features: typing.Dict[str, Feature] = {}


    def step(self):
        for k, f in self.features.items():
            f.update(self.market_data)
            self.history[k].append(f.value)

        try:
            self.decide_actions()
        except CantOpenPosition:
            pass

        self.account.step()


    def decide_actions(self):
        raise NotImplementedError

    def warm_up(self, ds: PriceDataset):
        old_market_data = self.market_data
        old_acc = self.account
        self.account = Mock()

        self.market_data = SimMarket(ds, ds.delta)
        def pass_foo(*args, **kwargs):
            pass

        self.decide_actions = pass_foo
        for _, low, high in ds:
            self.market_data.set_prices(low, high)
            self.step()
        self.market_data = old_market_data
        self.account = old_acc
        del self.decide_actions


    def max_long_amount(self):

        free_money = self.account.balance - self.account.risk()
        risk_per_unit = self.market_data.ask - self.market_data.lowest

        return free_money / risk_per_unit


    def max_short_amount(self):
        free_money = self.account.balance - self.account.risk()
        risk_per_unit = self.market_data.highest - self.market_data.bid

        return free_money / risk_per_unit