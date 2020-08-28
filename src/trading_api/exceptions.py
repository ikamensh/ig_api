class LoginError(Exception):
    pass


class CantOpenPosition(Exception):
    pass


class MarketClosedException(Exception):
    pass


class InvalidBoundingPriceException(CantOpenPosition):
    pass


class InsufficientFundsException(CantOpenPosition):
    pass


class PositionTooSmall(CantOpenPosition):
    pass

class MarketNotFoundError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass


class QuotaError(Exception):
    pass