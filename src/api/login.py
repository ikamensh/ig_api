import requests

from const import demo_url

key = "ab3e4a55c5f40b911bbf045d43846f7ba70103bc"
headers = {
    "X-IG-API-KEY": key
}
login_url = demo_url + "session"


def login():
    body = {
        "identifier": "ikamen_demo",
        "password": "Ngrt52wsd",
        "encryptedPassword": None
    }
    r = requests.post(url=login_url, headers=headers, json=body)
    if r.status_code != 200:
        raise Exception(f"Failed to login: {r.text}")

    return r.headers["cst"], r.headers["x-security-token"]


cst, seq_token = login()
headers["cst"] = cst
headers["x-security-token"] = seq_token
