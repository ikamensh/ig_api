# import pytest
# from unittest.mock import Mock, create_autospec
#
# import loguru
#
# import markets
# from trading_api.data_model.acc_detail import AccountDetails
# from trading_api.data_model.market_data import MarketData
# from trading_api.abstract_session import Session
# from launchers import startup
#
#
#
# @pytest.fixture()
# def loguru_no_sinks(monkeypatch):
#     monkeypatch.setattr(loguru.logger, "add", Mock())
#     yield
#
#
# @pytest.fixture()
# def mock_sess():
#     sess = create_autospec(Session, instance=True)
#
#     sess.price_history.return_value.__iter__.return_value = [("2019-06-30 21:00:00", (10, 20, 1))]
#     sess.get_positions.return_value = []
#
#     sess.get_acc_details.return_value = AccountDetails(
#         balance=5000,
#         profit_loss=0,
#         available=5000,
#         name="MockusGrandus",
#         id="12345",
#         currency="RMB!",
#     )
#
#     sess.get_market_data.return_value = MarketData(markets.vix.code, 10, 20, 5, 25, 0.2, "5 O'Clock")
#
#     yield sess
#
#
# def test_step(mock_sess, loguru_no_sinks):
#     """Verifies that startup.step does interacts with key methods of a session. """
#
#     startup._session_factory = lambda: mock_sess
#     startup.step()
#
#     assert mock_sess.get_acc_details.called
#     assert mock_sess.price_history.called
#     assert mock_sess.price_history.return_value.__iter__.called
#     assert mock_sess.get_positions.called
#
#
# def test_launch(mock_sess, monkeypatch, loguru_no_sinks):
#     """ Verify that launch does multiple interactions with session. """
#
#     monkeypatch.setattr(startup, "_session_factory", lambda: mock_sess)
#     N_ATTEMPTS = 2
#
#     import time
#
#     class ExpectedException(Exception):
#         pass
#
#     ctr = 0
#     def mock_sleep(*args):
#         nonlocal ctr
#         ctr += 1
#         if ctr == N_ATTEMPTS:
#             raise ExpectedException
#
#     monkeypatch.setattr(time, "sleep", mock_sleep)
#
#     with pytest.raises(ExpectedException):
#         startup.launch()
#
#     assert mock_sess.get_acc_details.call_count >= N_ATTEMPTS
#     assert mock_sess.price_history.call_count >= N_ATTEMPTS
#     assert mock_sess.price_history.return_value.__iter__.call_count >= N_ATTEMPTS
#     assert mock_sess.get_positions.call_count >= N_ATTEMPTS
#
#
# def test_buys_low(mock_sess, loguru_no_sinks):
#
#     startup._session_factory = lambda: mock_sess
#     mock_sess.get_market_data.return_value = MarketData(markets.vix.code, 3, 3.08, 3, 5, 0.2, "5 O'Clock")
#     startup.step()
#
#     assert mock_sess.open_position.call_count == 1
#     call = mock_sess.open_position.call_args_list[0]
#
#     amount, market_code, limit, stop = call.args
#     assert amount > 0
#
#
# def test_sells_high(mock_sess, loguru_no_sinks):
#     startup._session_factory = lambda: mock_sess
#     mock_sess.get_market_data.return_value = MarketData(markets.vix.code, 70, 73.08, 70, 75, 0.2,
#                                                         "5 O'Clock")
#     startup.step()
#
#     assert mock_sess.open_position.call_count == 1
#     call = mock_sess.open_position.call_args_list[0]
#
#     amount, market_code, limit, stop = call.args
#     assert amount < 0
#
