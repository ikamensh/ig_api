import typing
import markets
from loguru import logger

from api.abstract_session import Session
from api.data_model.position import Position
from datasets.market_history import MarketHistory
from exceptions import CantOpenPosition
from sim._sim_market_data import SimMarket

if typing.TYPE_CHECKING:
    from robotrader.features.features import Feature


class BoundsEstimate:
    def __init__(self, sess: Session):
        self._sess = sess
        self._lows = {}
        self._highs = {}

    def set_low(self, market_code: str, val: float):
        self._lows[market_code] = val

    def set_high(self, market_code: str, val: float):
        self._highs[market_code] = val

    def low(self, market_code: str):
        if market_code not in self._lows:
            self._lows[market_code] = 0
        return self._lows[market_code]

    def high(self, market_code: str):
        if market_code not in self._highs:
            price = self._sess.get_market_data(market_code).ask
            self._highs[market_code] = price * 10
        return self._highs[market_code]



class RoboTrader:
    def __init__(
        self, sess: Session, target_market: markets.MarketId, steps_per_day: int = None
    ):
        self.sess = sess
        self.market = target_market
        self.steps_per_day = steps_per_day
        self.features: typing.Dict[str, Feature] = {}
        self.bounds = BoundsEstimate(sess)

    def step(self):
        logger.debug(f"{self.__class__.__name__} is updating features.")
        for k, f in self.features.items():
            data = self.sess.get_market_data(self.market)
            f.update(data)
            logger.debug(f"{k: <15} = {f.value:.3f}")
        try:
            self.decide_actions()
        except CantOpenPosition:
            pass

    def beta_days(self, days):
        return 1 - 0.6 / days / self.steps_per_day

    def decide_actions(self):
        raise NotImplementedError

    def warm_up(self, ds: MarketHistory):
        logger.info(
            f"Running warmup on {ds} ({len(ds)=}, {ds.steps_per_day=}, {ds.start=}, {ds.end=})"
        )
        logger.disable(__name__)

        market_data = SimMarket(None)

        for low, high, delta in ds:
            market_data.set_prices(low, high, delta)
            for k, f in self.features.items():
                f.update(market_data)

        logger.enable(__name__)

        logger.debug(f"{self.__class__.__name__} updated features via warmup.")
        for k, f in self.features.items():
            logger.debug(f"{k: >15} = {f.value:.3f}")

    def _pos_risk(self, position):
        """Amount of worst-case loss due to this position. """
        if position.amount > 0:
            return position.amount * (position.price - self.bounds.low(position.market_data.market_id.code))
        else:
            return abs(position.amount) * (self.bounds.high(position.market_data.market_id.code) - position.price)

    def _risk(self):
        return sum([self._pos_risk(p) for p in self.sess.get_positions()])

    def _free_money(self):
        return self.sess.get_acc_details().available - self._risk()

    def max_long_amount(self):

        data = self.sess.get_market_data(self.market)
        risk_per_unit = data.ask - self.bounds.low(self.market.code)
        return self._free_money() / risk_per_unit

    def max_short_amount(self):

        data = self.sess.get_market_data(self.market)
        risk_per_unit = self.bounds.high(self.market.code) - data.bid
        return self._free_money() / risk_per_unit

    def market_data(self, market_code = None):
        market_code = market_code or self.market.code
        return self.sess.get_market_data(market_code)

    @property
    def positions(self):
        return self.sess.get_positions()

    @property
    def balance(self):
        return self.sess.get_acc_details().balance

    @property
    def available(self):
        return self.sess.get_acc_details().available

    @property
    def profit(self):
        return self.sess.get_acc_details().profit_loss

    def close(self, pos: Position):
        self.sess.close_position(pos)

    def open(self, amount, limit = None, stop = None):
        return self.sess.open_position(amount, self.market.code, limit, stop)
