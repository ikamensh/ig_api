import collections

import typing

if typing.TYPE_CHECKING:
    from src.robotrader.account import Platform

class Feature:
    value: float
    last_step: int = 0
    fn: typing.Callable = None

    def update(self, platform: "Platform"):
        if isinstance(self.fn, Feature):
            self.fn.update(platform)
        if self.last_step < platform.step:
            self.update_once(platform)
            self.last_step = platform.step

    def update_once(self, platform: "Platform"):
        pass

    def __call__(self, platform: "Platform"):
        self.update(platform)
        return self.value

def variance(pform):
    return ((pform.high_bid + pform.high_ask - pform.low_ask - pform.low_bid) / 4) ** 2

def price(platform):
    return (platform.market_ask + platform.market_bid) / 2

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
    def __init__(self, beta, fn: typing.Callable[["Platform"], float]):
        assert 0.5 < beta < 1
        self.beta = beta
        self.value = None
        self.fn = fn
        self.count = 0
        self.warm_up_buf = []

    def update_once(self, platform: "Platform"):
        if self.count < 10:
            self.warm_up_buf.append(self.fn(platform))
            self.value = sum(self.warm_up_buf) / len(self.warm_up_buf)
            self.count += 1
        else:
            self.value = self.beta * self.value + self.fn(platform) * (1 - self.beta)


class WindowVariance(Feature):
    def __init__(self, n: int):
        self.memory = collections.deque(maxlen=n*2)

    def update_once(self, platform: "Platform"):
        self.memory.extend( low_high(platform) )

    @property
    def value(self):
        return ( max(self.memory) - min(self.memory) ) ** 2


class Momentum(Feature):
    def __init__(self, fn):
        self.fn = fn
        self.last_val = None
        self.value = 0

    def update_once(self, platform: "Platform"):
        if self.last_val:
            self.value = self.fn(platform) - self.last_val
        self.last_val = self.fn(platform)


class MovingAvg(Feature):
    def __init__(self, n, fn: typing.Callable[["Platform"], float]):
        self.memory = collections.deque(maxlen=n)
        self.fn = fn

    def update_once(self, platform: "Platform"):
        self.memory.append(self.fn(platform))

    @property
    def value(self):
        return sum(self.memory) / len(self.memory)
