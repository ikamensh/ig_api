import collections
import typing
import datetime

from api.data_model.market_data import MarketData


class Feature:
    """ A feature that derives it's value from current and past values of MarketData.

    Designed to support compositional features by putting another feature into `fn` attribute of a parent feature.
    """

    value: float
    last_step: datetime = datetime.datetime(year=1970, month=1, day=1)
    fn: typing.Callable = None

    def update(self, market_data: "MarketData"):
        if isinstance(self.fn, Feature):
            self.fn.update(market_data)

        if self.last_step < market_data.time:
            self.update_once(market_data)
            self.last_step = market_data.time

    def update_once(self, platform: "MarketData"):
        pass

    def __call__(self, platform: "MarketData"):
        self.update(platform)
        return self.value


def price(market_data: MarketData):
    return (market_data.ask + market_data.bid) / 2


class Pow(Feature):
    def __init__(self, fn, pow):
        self.pow = pow
        self.fn: Feature = fn

    @property
    def value(self):
        return self.fn.value ** self.pow


class ExpAvg(Feature):
    def __init__(self, beta, fn: typing.Callable[["MarketData"], float]):
        """
        Args:
            beta: what fraction of old value is kept at each update. High beta = slow moving avg
            fn: the function or Feature to apply averaging to.
        """

        # Hack for genetic algorithms.
        if beta < 0:
            beta = abs(beta)

        if not 0.5 < beta < 1:
            beta = 0.75

        # start up - initially beta will be low, and will approach true value with time.
        self.true_beta = beta
        self.beta = 0.01
        self.value = None
        self.fn = fn

    def update_once(self, platform: "MarketData"):
        if self.value is None:
            self.value = self.fn(platform)

        beta_beta = 0.5 * self.true_beta + 0.5 * self.beta
        self.beta = beta_beta * self.beta + self.true_beta * (1 - beta_beta)
        self.value = self.beta * self.value + self.fn(platform) * (1 - self.beta)


def low_high(market_data: MarketData):
    return market_data.low, market_data.high


class WindowVariance(Feature):
    def __init__(self, n: int):
        self.memory = collections.deque(maxlen=1 + int(abs(n)) * 2)

    def update_once(self, market_data: "MarketData"):
        self.memory.extend(low_high(market_data))

    @property
    def value(self):
        return (max(self.memory) - min(self.memory)) ** 2


class Momentum(Feature):
    def __init__(self, fn, steps_per_day):
        self.fn = fn
        self.last_val = None
        self.value = 0
        self.steps_per_day = steps_per_day

    def update_once(self, market_data: "MarketData"):
        if self.last_val:
            self.value = self.steps_per_day * (self.fn(market_data) - self.last_val)
        self.last_val = self.fn(market_data)


class MovingAvg(Feature):
    def __init__(self, n, fn: typing.Callable[["MarketData"], float]):
        self.memory = collections.deque(maxlen=n)
        self.fn = fn

    def update_once(self, market_data: "MarketData"):
        self.memory.append(self.fn(market_data))

    @property
    def value(self):
        return sum(self.memory) / len(self.memory)
