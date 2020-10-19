import pytest


def test_sentiment(ig_session):
    long = ig_session.sentiment("US500")
    assert long > 0


def test_sentiment_wrong(sess):
    with pytest.raises(Exception):
        long = sess.sentiment("JUPITER_5000")


def test_sentiment_multiple(ig_session):
    keys = ["US500", "VOLIN", "EUVIX"]
    sentiments = ig_session.sentiments(keys)
    assert len(sentiments) == 3
    for k in keys:
        v = sentiments[k]
        assert v > 0
