import os

from api.get_history import write_history
from config import data_folder
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

    with open(history_path, "a", newline="") as csvfile:
        write_history(vix.code, csvfile, start_date=d)


update_history()
rt = ExpAvgTrader()

