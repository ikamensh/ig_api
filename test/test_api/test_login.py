from api.exceptions import LoginError
from api.ig_session import IgSession

import pytest

demo_account_id = "ikamen_demo"
demo_key = "ab3e4a55c5f40b911bbf045d43846f7ba70103bc"
demo_password = "BoringPassword123"

def test_login():
    sess = IgSession(demo_account_id, demo_key, demo_password)
    assert sess.headers["x-security-token"]


def test_login_bad_password():
    with pytest.raises(LoginError):
        sess = IgSession(demo_account_id, demo_key, "WrongPassword")

def test_login_bad_key():
    with pytest.raises(LoginError):
        sess = IgSession(demo_account_id, "WrongKey", demo_password)


