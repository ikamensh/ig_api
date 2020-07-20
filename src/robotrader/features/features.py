import collections
import typing

from env.real.market_data import RealMarket

if typing.TYPE_CHECKING:
    from env.abc.market_data import MarketData


class Feature:
    value: float
    last_step: int = 0
    fn: typing.Callable = None

    def update(self, market_data: "MarketData"):
        if isinstance(self.fn, Feature):
            self.fn.update(market_data)

        if isinstance(market_data, RealMarket):
            self.update_once(market_data)
        elif self.last_step < market_data.step: # assuming the market data to be SimMarket
            self.update_once(market_data)
            self.last_step = market_data.step

    def update_once(self, platform: "MarketData"):
        pass

    def __call__(self, platform: "MarketData"):
        self.update(platform)
        return self.value

def variance(market_data):
    return ((market_data.high_bid + market_data.high_ask - market_data.low_ask - market_data.low_bid) / 4) ** 2

def price(market_data):
    return (market_data.ask + market_data.bid) / 2

def low_high(platform):
    return (platform.high_ask + platform.high_bid) / 2, (platform.low_bid + platform.low_ask) / 2


class Pow(Feature):
    def __init__(self, fn, pow):
        self.pow = pow
        self.fn: Feature = fn

    @property
    def value(self):
        return self.fn.value ** self.pow


class ExpAvg(Feature):
    def __init__(self, beta, fn: typing.Callable[["MarketData"], float]):
        if beta < 0:
            beta = abs(beta)

        if not 0.5 < beta < 1:
            beta = 0.75

        self.beta = beta
        self.value = None
        self.fn = fn
        self.count = 0
        self.warm_up_buf = []

    def update_once(self, platform: "MarketData"):
        if self.count < 10:
            self.warm_up_buf.append(self.fn(platform))
            self.value = sum(self.warm_up_buf) / len(self.warm_up_buf)
            self.count += 1
        else:
            self.value = self.beta * self.value + self.fn(platform) * (1 - self.beta)


class WindowVariance(Feature):
    def __init__(self, n: int):
        self.memory = collections.deque(maxlen=1 + int(abs(n))*2)

    def update_once(self, platform: "MarketData"):
        self.memory.extend( low_high(platform) )

    @property
    def value(self):
        return ( max(self.memory) - min(self.memory) ) ** 2


class Momentum(Feature):
    def __init__(self, fn):
        self.fn = fn
        self.last_val = None
        self.value = 0

    def update_once(self, platform: "MarketData"):
        if self.last_val:
            self.value = self.fn(platform) - self.last_val
        self.last_val = self.fn(platform)


class MovingAvg(Feature):
    def __init__(self, n, fn: typing.Callable[["MarketData"], float]):
        self.memory = collections.deque(maxlen=n)
        self.fn = fn

    def update_once(self, platform: "MarketData"):
        self.memory.append(self.fn(platform))

    @property
    def value(self):
        return sum(self.memory) / len(self.memory)
