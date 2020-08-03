import markets
from api.data_model.snapshot import Snapshot


def test_gets_data(sess):
    snap, margin_req = sess._get_market_data(markets._VIX)
    assert isinstance(snap, Snapshot)
