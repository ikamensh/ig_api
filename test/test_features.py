import math

from src.robotrader.features.features import *

def test_exp_avg(platform):
    f = ExpAvg(0.75, price)
    values = []
    for p in range(25):
        platform.set_prices(low_ask=p, low_bid=p, high_ask=p, high_bid=p)
        f.update(platform)
        values.append(f.value)

    for i in range(len(values) - 1):
        assert values[i] < values[i+1]

    assert 15 < f.value < 25


def test_window_var_macro(platform):
    f = WindowVariance( int(30 * math.pi) )

    for i in range( int(30 * math.pi) ):
        p = math.sin(i/10)
        platform.set_prices(low_ask=p, low_bid=p, high_ask=p, high_bid=p)
        f.update(platform)

    assert math.isclose(f.value, 4, rel_tol=1e-1)


def test_window_var_micro(platform):
    f = WindowVariance( int(30 * math.pi) )

    for i in range( int(30 * math.pi) ):
        p = math.sin(i/10)
        platform.set_prices(low_ask=1, low_bid=1, high_ask=2+p, high_bid=2+p)
        f.update(platform)

    assert math.isclose(f.value, 4, rel_tol=1e-1)