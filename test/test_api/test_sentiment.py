import pytest


def test_sentiment(ig_session):
    long = ig_session.sentiment("US500")
    assert long > 0


def test_sentiment_wrong(sess):
    with pytest.raises(Exception):
        long = sess.sentiment("JUPITER_5000")