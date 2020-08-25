"""Launches a robotrader in produciton. """

import time

from loguru import logger

import markets
from datasets.market_history import MarketHistory
from datasets.resolutions import Resolutions
from trading_api.ig.ig_session import IgSession
from robotrader.traders.exp_avg import ExpAvgTrader
from resources.credentials import account_id, key, password



def _session_factory():
    return IgSession(account_id, key, password)


@logger.catch(reraise=True)
def step():
    """Independent action step - login, use history to warm up features, do actions."""

    sess = _session_factory()

    resolution = Resolutions.HOUR_2
    history = MarketHistory.from_csv(markets.vix)
    history.update(sess, resolution=resolution)

    target_market = markets.vix
    rt = ExpAvgTrader(
        sess, market_id=target_market, steps_per_day=history.steps_per_day
    )
    rt.warm_up(history)

    rt.decide_actions()


def launch():
    """ Error - resistant loop: do steps every 2 hours, retry on any exceptions. """

    log_format = (
        "<level>{message: <75}</level> - <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    )

    logger.add("startup_{time}.log", format=log_format)

    last_exception = None
    counter = 0
    retry_timer = 10

    while True:
        print("tick!")
        try:
            step()
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt. Shutting down.")
            break
        except Exception as e:
            if str(e) == last_exception:
                counter += 1
                logger.info(f"Retry pause for {retry_timer} seconds.")
                time.sleep(retry_timer)
                retry_timer *= 3
                if counter == 5:
                    logger.error(f"Failed with {e} 5 times - terminating.")
                    raise
            else:
                last_exception = str(e)
            msg = f"Exception {e} occured"
            if counter > 1:
                msg += f" {counter} times"
            logger.warning(msg)
        else:
            counter = 0
            retry_timer = 10

        logger.info("Sleeping for 2 hours.")
        time.sleep(7200)
