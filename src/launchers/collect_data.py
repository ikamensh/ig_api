from datetime import datetime, timedelta

from datasets.market_history import MarketHistory
from datasets.resolutions import Resolutions
from resources.credentials import account_id, password, gen_keys
from trading_api.ig.ig_session import IgSession

sess = IgSession(account_id, gen_keys(), password)

import markets



ds = MarketHistory.from_csv(markets.gold, Resolutions.MINUTE_10)
# start = ds.start - timedelta(days=14)
# end = ds.start
# ds.update(sess, start=start, end=end)
# ds.update(sess, start=datetime.now() - timedelta(days=90))
ds.update(sess, start=datetime.min, end=ds.start)
ds.to_csv()

