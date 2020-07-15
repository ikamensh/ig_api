import types
import datetime

import markets
from api.data_model.market_history import Resolutions


def test_price_history(sess):

    start = datetime.datetime(year=2019, month=7, day=2)
    end = start + datetime.timedelta(days=1)

    history_gen = sess.price_history(markets.vix.code,
                                     resolution=Resolutions.HOUR_2,
                                     start = start,
                                     end=end)

    assert isinstance(history_gen, types.GeneratorType)

    vals = list(history_gen)
    assert vals
