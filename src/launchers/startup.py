import time

from loguru import logger

import markets
from datasets.market_history import MarketHistory
from api.ig.ig_session import IgSession
from resources.credentials import account_id, key, password
from robotrader.traders.exp_avg import ExpAvgTrader

VIX_MIN_PRICE = 10
VIX_HIGH_PRICE = 110

@logger.catch(reraise=True)
def startup():
    sess = IgSession(account_id, key, password)

    history = MarketHistory.from_csv(markets.vix)
    history.update(sess)

    target_market = markets.vix
    rt = ExpAvgTrader(sess, market_id=target_market, steps_per_day=history.steps_per_day)
    rt.bounds.set_low(target_market.code, VIX_MIN_PRICE)
    rt.bounds.set_high(target_market.code, VIX_HIGH_PRICE)
    rt.warm_up(history)

    rt.decide_actions()

if __name__ == "__main__":

    log_format = ("<level>{message: <75}</level> - <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                  "<level>{level: <8}</level> | "
                  "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>")

    logger.add("startup_{time}.log", format=log_format)

    while True:
        try:
            print("tick!")
            startup()
        except Exception as e:
            print(e)
        logger.info("Sleeping for 2 hours.")
        time.sleep(7200)


