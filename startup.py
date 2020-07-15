import time

from loguru import logger

import config
import markets
from api.data_model.market_history import MarketHistory
from api.ig_session import IgSession
from credentials import account_id, key, password
from datasets.historical import get_ig_vix_ds
from env.real.account import RealAccount
from robotrader.traders.exp_avg import ExpAvgTrader
from api.write_history import resolutions

VIX_MIN_PRICE = 10
VIX_HIGH_PRICE = 110

@logger.catch(reraise=True)
def startup():
    sess = IgSession(account_id, key, password)

    mh = MarketHistory(markets.vix, resolution=resolutions.HOUR_2)
    mh.update(sess)


    vix_market = sess.get_market_data(markets.VIX)
    vix_market.lowest = VIX_MIN_PRICE
    vix_market.highest = VIX_HIGH_PRICE

    STEPS_PER_DAY = 9

    log = []
    acc = RealAccount(sess, log)

    rt = ExpAvgTrader(acc, market_data=vix_market, steps_per_day=STEPS_PER_DAY)
    vix_ds = get_ig_vix_ds()
    rt.warm_up(vix_ds)

    rt.decide_actions()
    for msg in log:
        print(msg)

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
        time.sleep(7200)


