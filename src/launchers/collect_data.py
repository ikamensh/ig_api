from datetime import datetime, timedelta

from datasets.market_history import MarketHistory
from datasets.resolutions import Resolutions
from resources.credentials import account_id, password, extra_keys
from trading_api.ig.ig_session import IgSession

key = extra_keys[0]

sess = IgSession(account_id, key, password)

import markets



ds = MarketHistory.from_csv(markets.vix, Resolutions.MINUTE)
# start = ds.start - timedelta(days=14)
# end = ds.start
# ds.update(sess, start=start, end=end)
ds.update(sess, start=datetime.min, end=ds.start)
ds.to_csv()

