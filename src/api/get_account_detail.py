import requests

from api.login import headers
from const import demo_url

acc_url = demo_url + "accounts/"


class AccountDetails:
    def __init__(self, json_elem):
        self.balance = float(json_elem["balance"]["balance"])
        self.name = json_elem["accountName"]
        self.id = json_elem["accountId"]
        self.currency = json_elem["currency"]

    def __repr__(self):
        return f"Account {self.id} | {self.name} with balance {self.balance} {self.currency}"


def get_acc_details() -> AccountDetails:
    r = requests.get(url=acc_url, headers=headers)
    assert r.status_code == 200

    target_name = "CFD"
    for acc in r.json()["accounts"]:
        if acc["accountName"] == target_name:
            return AccountDetails(acc)

    raise Exception("Account not found.")


if __name__ == "__main__":
    print(get_acc_details())
