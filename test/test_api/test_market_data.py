import pytest

from ig_api import markets
from ig_api.data_model.snapshot import Snapshot
from ig_api.exceptions import MarketNotFoundError


def test_gets_data(ig_session):
    snap, margin_req = ig_session._get_market_data(markets._VIX)
    assert isinstance(snap, Snapshot)



def test_unknown_market(sess):
    with pytest.raises(MarketNotFoundError):
        snap, margin_req = sess.get_market_data("UNKNOWN_MARKET")
