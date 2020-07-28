from datasets.historical import cboe_vix, ig_vix, ig_vix_eu

def test_cboe():
    assert len(cboe_vix) > 100
    assert cboe_vix.steps_per_day == 1

def test_ig_vix():
    assert len(ig_vix) > 100
    assert ig_vix.steps_per_day > 1
    assert ig_vix.steps_per_day < 24

def test_ig_vix_eu():
    assert len(ig_vix_eu) > 100
    assert ig_vix_eu.steps_per_day > 1
    assert ig_vix_eu.steps_per_day < 24