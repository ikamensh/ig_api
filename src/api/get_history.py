import requests
import datetime
import csv

from const import demo_url
import markets
from src.api.login import headers

prices_url = demo_url + "prices/"


class resolutions:
    MINUTE_30 = "MINUTE_30"
    HOUR_2 = "HOUR_2"


def price_history(market, res, start, end):
    if isinstance(start, datetime.datetime):
        start = start.isoformat()

    if isinstance(end, datetime.datetime):
        end = start.isoformat()
    assert isinstance(start, str)
    assert isinstance(end, str)


    headers["Version"] = "3"

    payload = {
        "resolution": res,
        "from": start,
        "to": end,
        "pageSize":500
    }
    r = requests.get(url=prices_url + market, headers=headers, params=payload)
    if r.status_code != 200:
        raise Exception(f"API error: {r.text}")

    n_pages = r.json()["metadata"]["pageData"]["totalPages"]
    init_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]

    for page in range(1, n_pages + 1):
        payload["pageNumber"] = page
        r = requests.get(url=prices_url + market, headers=headers, params=payload)
        if r.status_code != 200:
            raise Exception(f"API error: {r.text}")

        j = r.json()
        if "prices" in j:
            for p in j["prices"]:
                t = p["snapshotTimeUTC"]

                elem = t, p["lowPrice"]["bid"], p["lowPrice"]["ask"], p["highPrice"]["bid"], p["highPrice"]["ask"]
                if all(x is not None for x in elem):
                    yield elem

    else:
        rem_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]
        print(f"Used allowance: {init_allowance - rem_allowance}, remaining: {rem_allowance}")


    del headers["Version"]


def write_history(market, file, start_date, end_date = None):
    writer = csv.writer(
        file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )

    end = end_date or datetime.datetime.now()
    start = start_date
    for i, v in enumerate(
            price_history(
                market, resolutions.HOUR_2, start.isoformat(), end.isoformat()
            )
    ):
        if not i % 10:
            print(i)
        writer.writerow(v)

if __name__ == "__main__":
    from config import data_folder

    with open(data_folder +  "/ig_vix.csv", "w", newline="") as csvfile:
        start = datetime.datetime.now() - datetime.timedelta(days=365)
        write_history(markets.VIX, csvfile, start)

