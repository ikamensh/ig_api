from ig_api.datasets.synthetic.fade_over import fadeover_4_years, fadeover_1_year
from ig_api.datasets.synthetic.random_slice import random_slice


def test_default_slice():
    ds = random_slice(years=1)
    assert ds.steps_per_day > 1
    assert len(ds) > 30 * ds.steps_per_day


def test_fadeover_1():
    ds = fadeover_1_year()
    assert ds.steps_per_day > 1
    assert len(ds) > 30 * ds.steps_per_day


def test_fadeover_4():
    ds = fadeover_4_years()
    assert ds.steps_per_day > 1
    assert len(ds) > 30 * ds.steps_per_day

