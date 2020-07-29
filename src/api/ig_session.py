import datetime

import requests
import contextlib
from typing import List

from api.data_model.acc_detail import AccountDetails
from env.real.position import RealPosition
from env.sim.position import Position
from api.exceptions import LoginError
from api.data_model.snapshot import Snapshot
from env.real.market_data import RealMarket
from loguru import logger

_demo_url = "https://demo-api.ig.com/gateway/deal/"


class IgSession:
    def __init__(self, identifier, key, password, demo=True):
        self.master_url = _demo_url if demo else None

        headers = {"X-IG-API-KEY": key}

        login_url = self.master_url + "session"

        body = {
            "identifier": identifier,
            "password": password,
            "encryptedPassword": None,
        }
        r = requests.post(url=login_url, headers=headers, json=body)
        if r.status_code != 200:
            raise LoginError(f"Failed to login: {r.text}")

        headers["cst"] = r.headers["cst"]
        headers["x-security-token"] = r.headers["x-security-token"]

        self.headers = headers
        self._latest_prices = {}
        logger.info(f"Successfully logged in as {identifier} to {self.master_url}")

    @contextlib.contextmanager
    def use_version(self, version: int):
        self.headers["Version"] = str(version)
        yield
        del self.headers["Version"]

    @contextlib.contextmanager
    def use_method(self, method: str):
        self.headers["_method"] = method
        yield
        del self.headers["_method"]

    def _get_market_data(self, market) -> RealMarket:
        markets_url = self.master_url + "markets/"

        with self.use_version(3):
            r = requests.get(url=markets_url + market, headers=self.headers)

        assert r.status_code == 200
        reply = r.json()
        snap = Snapshot(reply["snapshot"])
        instrument_el = reply["instrument"]
        dealing_rules = reply["dealingRules"]

        market_id = instrument_el["epic"]
        assert instrument_el["marginFactorUnit"] == "PERCENTAGE"
        margin_req = float(instrument_el["marginFactor"]) / 100

        return RealMarket(
            market_id=market_id, bid=snap.bid, ask=snap.offer, margin_req=margin_req
        )

    def get_positions(self) -> List[Position]:
        positions_url = self.master_url + "positions/"

        with self.use_version(2):
            r = requests.get(url=positions_url, headers=self.headers)
        assert r.status_code == 200, r.text
        result = []
        for pos_elem in r.json()["positions"]:
            pos = pos_elem["position"]
            market = pos_elem["market"]

            amount = pos["size"]
            if pos["direction"] == "SELL":
                amount *= -1

            price = float(pos["level"])
            deal_id = pos["dealId"]

            market_id = market["epic"]
            market_name = market["instrumentName"]

            # can be expensive - we make API call for each new market we see.
            # Actual data is already in the response.
            pos = RealPosition(
                amount, self.get_market_data(market_id), deal_id=deal_id, price=price
            )
            result.append(pos)

        return result

    def get_market_data(self, market) -> RealMarket:
        if not market in self._latest_prices:
            price_data = self._get_market_data(market)
            self._latest_prices[market] = price_data

        return self._latest_prices[market]

    def _open_position(self, market, amount) -> str:
        otc_url = self.master_url + "positions/otc/"

        body = {
            "expiry": "-",
            "orderType": "MARKET",
            "timeInForce": None,
            "level": None,
            "guaranteedStop": "false",
            "stopLevel": None,
            "stopDistance": None,
            "trailingStop": None,
            "trailingStopIncrement": None,
            "forceOpen": "false",
            "limitLevel": None,
            "limitDistance": None,
            "quoteId": None,
            "currencyCode": "EUR",
            "epic": market,
            "size": abs(amount),
        }

        if amount < 0:
            body["direction"] = "SELL"
        else:
            body["direction"] = "BUY"
        with self.use_version(2):
            r = requests.post(url=otc_url, headers=self.headers, json=body)
        assert r.status_code == 200, r.json()

        return r.json()["dealReference"]

    def _deal_confirm(self, deal_reference) -> RealPosition:
        trade_confirm_url = self.master_url + "confirms/"

        r = requests.get(
            url=f"{trade_confirm_url}/{deal_reference}", headers=self.headers
        )
        assert r.status_code == 200, r.text

        reply = r.json()
        status, reason = reply["dealStatus"], reply["reason"]
        print(status, reason)

        if status != "ACCEPTED":
            raise Exception(f"Failed to open position, reason: {reason}.")

        deal_id = reply["dealId"]
        price = float(reply["level"])

        amount = int(reply["size"])
        if reply["direction"] == "SELL":
            amount *= -1

        market = reply["epic"]

        return RealPosition(
            amount=amount,
            market_data=self.get_market_data(market),
            price=price,
            deal_id=deal_id,
        )

    def open_position(self, amount: int, market: str) -> RealPosition:
        # TODO support limit & stop
        ref = self._open_position(market, amount)
        return self._deal_confirm(ref)

    def close_position(self, pos: RealPosition) -> None:
        otc_url = self.master_url + "positions/otc"

        body = {
            "dealId": pos.deal_id,
            "epic": None,
            "expiry": None,
            "level": None,
            "orderType": "MARKET",
            "timeInForce": None,
            "quoteId": None,
            "size": str(abs(int(pos.amount))),
        }

        if pos.amount < 0:
            body["direction"] = "BUY"
        else:
            body["direction"] = "SELL"

        with self.use_method("DELETE"), self.use_version(1):
            r = requests.post(url=otc_url, headers=self.headers, json=body)

        assert r.status_code == 200, r.text

    def get_acc_details(self) -> AccountDetails:
        acc_url = self.master_url + "accounts/"

        r = requests.get(url=acc_url, headers=self.headers)
        assert r.status_code == 200, r.json()

        target_name = "CFD"
        matches = []
        for acc in r.json()["accounts"]:
            if acc["accountName"] == target_name:
                matches.append(AccountDetails(acc))

        if not matches:
            raise Exception(f"Account not found. {r.json()}")

        if len(matches) > 1:
            raise Exception(f"Multiple accounts found.")

        return matches[0]

    def price_history(
        self,
        market: str,
        resolution: str,
        start: datetime.datetime,
        end: datetime.datetime,
    ):
        prices_url = self.master_url + "prices/"

        start = start.isoformat()
        end = end.isoformat()

        payload = {"resolution": resolution, "from": start, "to": end, "pageSize": 500}
        with self.use_version(3):
            r = requests.get(
                url=prices_url + market, headers=self.headers, params=payload
            )
            if r.status_code != 200:
                raise Exception(f"API error: {r.text}")

            n_pages = r.json()["metadata"]["pageData"]["totalPages"]
            init_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]

            for page in range(1, n_pages + 1):
                payload["pageNumber"] = page
                r = requests.get(
                    url=prices_url + market, headers=self.headers, params=payload
                )
                if r.status_code != 200:
                    raise Exception(f"API error: {r.text}")

                reply = r.json()
                if "prices" in reply:
                    for p in reply["prices"]:
                        timestamp = p["snapshotTimeUTC"]

                        prices = [
                            p["lowPrice"]["bid"],
                            p["lowPrice"]["ask"],
                            p["highPrice"]["bid"],
                            p["highPrice"]["ask"],
                        ]
                        if None in prices:
                            continue

                        prices = [float(x) for x in prices]
                        lb, la, hb, ha = prices
                        delta = ha - hb
                        low = (lb + la) / 2
                        high = (hb + ha) / 2

                        yield timestamp, low, high, delta

            else:
                rem_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]
                print(
                    f"Used allowance: {init_allowance - rem_allowance}, remaining: {rem_allowance}"
                )
