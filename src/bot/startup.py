import datetime
import os

from api.get_account_detail import get_acc_details
from api.get_history import write_history
from api.query_market import get_snapshot
from api.latest_prices import get_price_data
from config import data_folder
from datasets.historical import get_ig_vix_ds
from markets import vix
from robotrader.traders.exp_avg import ExpAvgTrader
from simulate import warm_up

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

STEPS_PER_DAY = 9
update_history()

log = []
acc_details = get_acc_details()
rt = ExpAvgTrader(balance=acc_details.balance, price_data=get_price_data(vix.code), log=log,
                  steps_per_day=9)

vix_ds = get_ig_vix_ds()
warm_up(rt, vix_ds)  # TODO move warm_up method to robotrader class


def fake_close(pos):
    print(f"Close {pos} ")

def fake_open(amt, limit=None, stop=None):
    print(f"Open position with amount {amt}, {limit=}, {stop=}")

acc = rt.account
acc.close = fake_close
acc.open = fake_open

snap = get_snapshot(vix.code)
rt.price_data.sync_snapshot(snap)

rt.decide_actions()
