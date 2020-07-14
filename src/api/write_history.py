import datetime
import csv

import markets
from api.ig_session import IgSession
from credentials import account_id, key, password


class resolutions:
    MINUTE_30 = "MINUTE_30"
    HOUR_2 = "HOUR_2"

def write_history(sess, market, file, start_date, end_date=None):
    writer = csv.writer(
        file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )

    end = end_date or datetime.datetime.now()
    start = start_date
    for i, v in enumerate(
            sess.price_history(
                market, resolutions.HOUR_2, start.isoformat(), end.isoformat()
            )
    ):
        if not i % 10:
            print(i)
        writer.writerow(v)


if __name__ == "__main__":
    from config import data_folder

    sess = IgSession(account_id, key, password)

    with open(data_folder + "/ig_vix.csv", "w", newline="") as csvfile:
        start = datetime.datetime.now() - datetime.timedelta(days=365)
        write_history(sess, markets.VIX, csvfile, start)
