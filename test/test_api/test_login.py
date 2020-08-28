from trading_api.exceptions import LoginError
from trading_api.ig.ig_session import IgSession

import pytest

demo_account_id = "ikamen_demo"
def keygen():
    yield "ab3e4a55c5f40b911bbf045d43846f7ba70103bc"
demo_password = "BoringPassword123"

def test_login():
    sess = IgSession(demo_account_id, keygen(), demo_password)
    assert sess._headers["x-security-token"]


def test_login_bad_password():
    with pytest.raises(LoginError):
        sess = IgSession(demo_account_id, keygen(), "WrongPassword")

def test_login_bad_key():
    def keygen():
        yield "WrongKey"

    with pytest.raises(LoginError):
        sess = IgSession(demo_account_id, keygen(), demo_password)


