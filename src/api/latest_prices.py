import markets
from api.query_market import get_snapshot
from env.price_data import PriceData

_latest_prices = {}

_vix_snap = get_snapshot(markets.VIX)

VIX_MIN_PRICE = 10
VIX_HIGH_PRICE = 110

_vix_price_data = PriceData(
    delta=_vix_snap.delta,
    market_id=_vix_snap.market,
    lowest=VIX_MIN_PRICE,
    highest=VIX_HIGH_PRICE,
)
_vix_price_data.sync_snapshot(_vix_snap)

_latest_prices[_vix_snap.market] = _vix_price_data


def get_price_data(market):
    if not market in _latest_prices:
        price_data = PriceData(market)
        snap = get_snapshot(market)
        price_data.sync_snapshot(snap)
        _latest_prices[market] = price_data
    return _latest_prices[market]
