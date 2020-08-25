import typing
import markets
from loguru import logger

from trading_api.abstract_session import Session
from trading_api.data_model.position import Position
from datasets.market_history import MarketHistory
from trading_api.exceptions import CantOpenPosition
from trading_api.sim._sim_market_data import SimMarket

if typing.TYPE_CHECKING:
    from robotrader.features.features import Feature


class BoundsEstimate:
    """Stores estimated lowest and highest probable values per market code."""

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


VIX_MIN_PRICE = 10
VIX_HIGH_PRICE = 75

class RoboTrader:
    """Abstract class for trading bot."""

    def __init__(
        self, sess: Session, target_market: str, steps_per_day: int = None
    ):
        """
        Args:
            sess: a Session object used to interact with the broker server.
            target_market: currently, a bot is doing trades only on a single market.
            steps_per_day:
                how many time per actual day will step function be called. Used to calibrate features.
        """
        assert isinstance(target_market, str)

        self.sess = sess
        self.market = target_market
        self.steps_per_day = steps_per_day
        self.features: typing.Dict[str, Feature] = {}
        self.bounds = BoundsEstimate(sess)

        # Built-in knowledge - VIX stayed for most of it's history between these two values.
        self.bounds.set_low(markets.vix.code, VIX_MIN_PRICE)
        self.bounds.set_high(markets.vix.code, VIX_HIGH_PRICE)

    def step(self):
        """Activate robotrader: update features, decide and execute actions.

        Currently all features target only a single market."""

        self.sess.update_market_data()
        logger.debug(f"{self.__class__.__name__} is updating features.")
        data = self.sess.get_market_data(self.market)

        for k, f in self.features.items():
            f.update(data)
            logger.debug(f"{k: <15} = {f.value:.3f}")
        try:
            self.decide_actions()
        except CantOpenPosition:
            pass

    def _beta_days(self, days: float):
        """Recommended coeficient for exponential average based on half-life in days. """

        return 1 - 0.6 / days / self.steps_per_day

    def decide_actions(self):
        raise NotImplementedError

    def warm_up(self, ds: MarketHistory):
        """Use a market history object to bring features to current values. """

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
            return position.amount * (position.price - self.bounds.low(position.market_data.market_code))
        else:
            return abs(position.amount) * (self.bounds.high(position.market_data.market_code) - position.price)

    def _risk(self):
        """Amount of worst-case loss due to all positions. """
        return sum([self._pos_risk(p) for p in self.sess.get_positions()])

    def _free_money(self):
        """Free money - available money now minus worst case losses. """
        return self.sess.get_acc_details().available - self._risk()

    def max_long_amount(self):
        """Maximum amount of volatility to be bought without risk of forced pos closures. """

        data = self.sess.get_market_data(self.market)
        risk_per_unit = max(1, data.ask - self.bounds.low(self.market))
        return self._free_money() / risk_per_unit

    def max_short_amount(self):
        """Maximum amount of volatility to be shorted without risk of forced position closures. """

        data = self.sess.get_market_data(self.market)
        risk_per_unit = max(1, self.bounds.high(self.market) - data.bid)
        return self._free_money() / risk_per_unit

    def market_data(self, market_code = None):
        """Get market data for target market code. Defaults to volatility. """
        market_code = market_code or self.market
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
        logger.info(f"Closing position {pos}")
        self.sess.close_position(pos)

    def open(self, amount, limit = None, stop = None):
        logger.info(f"Opening position {amount=} in market {self.market}")
        return self.sess.open_position(self.market, amount, limit, stop)

    def debug_info(self) -> typing.Dict[str, float]:
        return {}

