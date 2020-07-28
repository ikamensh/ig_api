import types
import datetime

import markets
from datasets.market_history import Resolutions


def test_price_history(sess):

    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)

    history_gen = sess.price_history(markets.vix.code,
                                     resolution=Resolutions.HOUR_2,
                                     start = start,
                                     end=end)

    assert isinstance(history_gen, types.GeneratorType)

    vals = list(history_gen)
    assert vals
