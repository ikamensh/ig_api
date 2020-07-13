import os

from api.get_history import write_history
from config import data_folder
from env.price_data import PriceData
from robotrader.traders.exp_avg import ExpAvgTrader

import datetime

from markets import vix

history_path = os.path.join(data_folder, vix.name + ".csv")


def get_latest_datetime(history_path):
    with open(history_path) as f:
        lines = f.readlines()

    for l in reversed(lines):
        if l.strip():
            date_str = l.split(',')[0]
            return datetime.datetime.fromisoformat(date_str)

def update_history():
    d = get_latest_datetime(history_path)
    d += datetime.timedelta(hours=2.5)

    with open(history_path, "a", newline="") as csvfile:
        write_history(vix.code, csvfile, start_date=d)


update_history()

log = []

from api.get_account_detail import AccountDetails, get_acc_details
acc_details = get_acc_details()
STEPS_PER_DAY = 9

from api.query_market import get_snapshot
snap = get_snapshot(vix.code)
price_data = PriceData(snap.offer - snap.bid)



rt = ExpAvgTrader(balance=acc_details.balance, price_data=price_data, log=log, steps_per_day=9)

from datasets.historical import get_ig_vix_ds

vix_ds = get_ig_vix_ds()
from simulate import warm_up
warm_up(rt, vix_ds)  # TODO move warm_up method to robotrader class

price = (snap.offer + snap.bid) / 2
price_data.set_prices(low=price, high=price)
acc = rt.account
# TODO read positions, add them to the account

def fake_close(pos):
    print(f"Close {pos} ")

def fake_open(amt, limit=None, stop=None):
    print(f"Open position with amount {amt}, {limit=}, {stop=}")

acc.close = fake_close
acc.open = fake_open

rt.decide_actions()


