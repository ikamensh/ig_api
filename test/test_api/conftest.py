import pytest

from api.ig.ig_session import IgSession

demo_account_id = "ikamen_demo"
demo_key = "ab3e4a55c5f40b911bbf045d43846f7ba70103bc"
demo_password = "BoringPassword123"

_sess = None

@pytest.fixture()
def sess():
    global _sess
    if _sess is None:
        _sess = IgSession(demo_account_id, demo_key, demo_password)
    yield _sess