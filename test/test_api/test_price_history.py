import types
import datetime

from ig_api import markets
from ig_api.datasets.resolutions import Resolutions


def test_price_history(sess):

    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365)

    history_gen = sess.price_history(markets.vix.code,
                                     resolution=Resolutions.HOUR_2,
                                     start = start,
                                     end=end)

    assert isinstance(history_gen, types.GeneratorType)

    val = next(history_gen)
    assert val
