import typing
from contextlib import contextmanager


class Platform:
    def __init__(self):
        self.high_bid = None
        self.high_ask = None

        self.low_bid = None
        self.low_ask = None

        self.market_ask = None
        self.market_bid = None
        self.delta = None
        self.step = 0

    def set_prices(self, *, low_bid, low_ask, high_bid, high_ask):
        assert low_ask >= low_bid
        assert high_ask >= high_bid
        self.low_ask = low_ask
        self.low_bid = low_bid
        self.delta = low_ask - low_bid

        self.high_ask = high_ask
        self.high_bid = high_bid

        self.market_bid = (high_bid + low_bid) / 2
        self.market_ask = (high_ask + low_ask) / 2
        self.step += 1

    @contextmanager
    def moment_prices(self, bid, ask):
        old_ask, old_bid = self.market_ask, self.market_bid
        self.market_ask = min( self.high_ask, max(self.low_ask, ask))
        self.market_bid = min( self.high_bid, max(self.low_bid, bid))
        yield
        self.market_ask, self.market_bid = old_ask, old_bid


class Position:
    id = 1
    MARGIN_REQ = 0.2

    def __init__(self, amount, platform: Platform, limit=None, stop=None):
        self.platform = platform
        ask, bid = platform.market_ask, platform.market_bid
        self.amount = amount

        if amount > 0:
            self.price = ask
            if limit:
                assert limit > self.price
            if stop:
                assert stop < self.price
        else:
            self.price = bid
            if limit:
                assert limit < self.price
            if stop:
                assert stop > self.price

        self.id = Position.id
        Position.id += 1

        self.limit = limit
        self.stop = stop

    def profit(self, *, mode="market"):
        if mode == "market":
            ask, bid = self.platform.market_ask, self.platform.market_bid
        elif mode == "high":
            ask, bid = self.platform.high_ask, self.platform.high_bid
        elif mode == "low":
            ask, bid = self.platform.low_ask, self.platform.low_bid
        else:
            raise Exception(f"invalid mode: {mode}")

        if self.amount > 0:
            cost = self.amount * self.price
            win = self.amount * bid
        else:
            win = abs(self.amount) * self.price
            cost = abs(self.amount) * ask
        return win - cost

    def margin(self):
        ask, bid = self.platform.market_ask, self.platform.market_bid
        value = abs(self.amount) * (bid + ask) / 2
        return self.MARGIN_REQ * value

    def __repr__(self):
        return f"Position {self.id} ({self.amount=})"


class InsufficientFundsException(Exception):
    pass


class Account:
    def __init__(self, platform: Platform, balance, log_fn=lambda x: x):
        self.balance = balance
        self.positions: typing.List[Position] = []
        self.pform = platform
        # self.log_fn = log_fn

    def margin(self):
        return sum(p.margin() for p in self.positions)

    def profit(self, mode="market"):
        return sum(p.profit(mode=mode) for p in self.positions)

    def available(self):
        return min(
            self.balance + self.profit(mode) - self.margin()
            for mode in ["low", "high", "market"]
        )

    def open(self, amt, limit = None, stop = None) -> Position:
        pos = Position(amt, self.pform, limit=limit, stop=stop)
        if self.available() >= pos.margin():
            self.positions.append(pos)
            return pos
        else:
            raise InsufficientFundsException

    def close(self, position: Position):
        assert position in self.positions
        profit = position.profit()
        self.balance += profit
        self.positions.remove(position)

    def step(self):
        self._ensure_margin()
        self.stop_limit()

    def stop_limit(self):
        for p in list(self.positions):
            if p.amount > 0:  # long
                if p.limit is not None and p.limit <= self.pform.high_bid:
                    with self.pform.moment_prices(
                            bid=p.limit, ask=p.limit + self.pform.delta
                    ):
                        self.close(p)

                elif p.stop is not None and p.stop >= self.pform.low_bid:
                    with self.pform.moment_prices(
                            bid=p.stop, ask=p.stop + self.pform.delta
                    ):
                        self.close(p)

            else:  # short
                if p.limit is not None and p.limit >= self.pform.low_ask:
                    with self.pform.moment_prices(
                            bid=p.limit - self.pform.delta, ask=p.limit
                    ):
                        self.close(p)

                elif p.stop is not None and p.stop < self.pform.high_ask:
                    with self.pform.moment_prices(
                            bid=p.stop - self.pform.delta, ask=p.stop
                    ):
                        self.close(p)

    def _ensure_margin(self):
        while self.available() < 0 and self.positions:
            pos = self.positions[-1]
            self.close(pos)
