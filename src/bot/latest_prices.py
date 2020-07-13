import markets
from api.query_market import get_snapshot
from env.price_data import PriceData

latest_prices = {}

vix_snap = get_snapshot(markets.VIX)

VIX_MIN_PRICE = 10
VIX_HIGH_PRICE = 110

vix_price_data = PriceData(
    delta=vix_snap.delta,
    market_id=vix_snap.market,
    lowest=VIX_MIN_PRICE,
    highest=VIX_HIGH_PRICE,
)
vix_price_data.sync_snapshot(vix_snap)

latest_prices[vix_snap.market] = vix_price_data
