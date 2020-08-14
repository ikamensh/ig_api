import math

from src.robotrader.features.features import *

def test_exp_avg(vix_price_data):
    f = ExpAvg(0.75, price)
    values = []
    for p in range(25):
        vix_price_data.set_prices(p, p, 1)
        f.update(vix_price_data)
        values.append(f.value)

    for i in range(len(values) - 1):
        assert values[i] < values[i+1]

    assert 15 < f.value < 25


def test_window_var_macro(vix_price_data):
    f = WindowVariance( int(30 * math.pi) )

    for i in range( int(30 * math.pi) ):
        p = math.sin(i/10)
        vix_price_data.set_prices(p, p, 1)
        f.update(vix_price_data)

    assert math.isclose(f.value, 4, rel_tol=1e-1)


def test_window_var_micro(vix_price_data):
    f = WindowVariance( int(30 * math.pi) )

    for i in range( int(30 * math.pi) ):
        p = math.sin(i/10)
        vix_price_data.set_prices(1, 2 + p, 1)
        f.update(vix_price_data)

    assert math.isclose(f.value, 4, rel_tol=1e-1)