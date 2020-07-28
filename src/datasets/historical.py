import markets
from datasets.market_history import MarketHistory

ig_vix = MarketHistory.from_csv(markets.vix)
ig_vix_eu = MarketHistory.from_csv(markets.vix_eu)
cboe_vix = MarketHistory.from_csv(markets.cboe_vix)
