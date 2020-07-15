from env.real.account import RealAccount


def test_init(sess):
    acc = RealAccount(sess)
    assert isinstance(acc, RealAccount)