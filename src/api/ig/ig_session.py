from datetime import datetime, timedelta

import requests
import contextlib
from typing import List, Generator, Tuple, Dict

from api.abstract_session import Session
from api.data_model.acc_detail import AccountDetails
from api.data_model.market_data import MarketData
from api.data_model.position import Position
from api.exceptions import LoginError
from api.data_model.snapshot import Snapshot
from loguru import logger

_demo_url = "https://demo-api.ig.com/gateway/deal/"


class IgSession(Session):
    UPDATE_FREQ = timedelta(minutes=3)

    def __init__(self, identifier, key, password, demo=True):
        self._master_url = _demo_url if demo else None

        self._headers = {"X-IG-API-KEY": key}
        self._login(identifier, password)
        self._latest_prices: Dict[str, MarketData] = {}

    def get_positions(self) -> List[Position]:
        positions_url = self._master_url + "positions/"

        with self._use_version(2):
            r = requests.get(url=positions_url, headers=self._headers)
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
            pos = Position(
                amount, self.get_market_data(market_id), deal_id=deal_id, price=price
            )
            result.append(pos)

        return result

    def get_market_data(self, market_code: str) -> MarketData:
        if not market_code in self._latest_prices:
            snap, margin_req = self._get_market_data(market_code)
            price_data = MarketData.from_snapshot(snap, market_code, margin_req)
            self._latest_prices[market_code] = price_data

        return self._latest_prices[market_code]

    def update_market_data(self):
        now = datetime.now()
        for md in self._latest_prices.values():
            if now - md.time > self.UPDATE_FREQ:
                snap, margin_req = self._get_market_data(md.market_code)
                md.update(snap)
                logger.debug(f"Updating market data: {md}.")

    def open_position(self, amount: int, market: str) -> Position:
        # TODO support limit & stop

        # TODO handle insufficient funds
        ref = self._open_position(market, amount)
        return self._deal_confirm(ref)

    def close_position(self, pos: Position) -> None:
        otc_url = self._master_url + "positions/otc"

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

        with self._use_method("DELETE"), self._use_version(1):
            r = requests.post(url=otc_url, headers=self._headers, json=body)

        assert r.status_code == 200, r.text

    def get_acc_details(self) -> AccountDetails:
        acc_url = self._master_url + "accounts/"

        r = requests.get(url=acc_url, headers=self._headers)
        assert r.status_code == 200, r.json()

        target_name = "CFD"
        matches = []
        for acc in r.json()["accounts"]:
            if acc["accountName"] == target_name:
                matches.append(AccountDetails.from_json(acc))

        if not matches:
            raise Exception(f"Account not found. {r.json()}")

        if len(matches) > 1:
            raise Exception(f"Multiple accounts found.")

        return matches[0]

    def price_history(
        self, market: str, resolution: str, start: datetime, end: datetime,
    ) -> Generator[Tuple[str, float, float, float], None, None]:
        prices_url = self._master_url + "prices/"

        start = start.isoformat()
        end = end.isoformat()

        payload = {"resolution": resolution, "from": start, "to": end, "pageSize": 500}
        with self._use_version(3):
            r = requests.get(
                url=prices_url + market, headers=self._headers, params=payload
            )
            if r.status_code != 200:
                raise Exception(f"API error: {r.text}")

            n_pages = r.json()["metadata"]["pageData"]["totalPages"]
            init_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]

            for page in range(1, n_pages + 1):
                payload["pageNumber"] = page
                r = requests.get(
                    url=prices_url + market, headers=self._headers, params=payload
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

    def _login(self, identifier, password):
        login_url = self._master_url + "session"
        body = {
            "identifier": identifier,
            "password": password,
            "encryptedPassword": None,
        }
        r = requests.post(url=login_url, headers=self._headers, json=body)
        if r.status_code != 200:
            raise LoginError(f"Failed to login: {r.text}")
        self._headers["cst"] = r.headers["cst"]
        self._headers["x-security-token"] = r.headers["x-security-token"]
        logger.info(f"Successfully logged in as {identifier} to {self._master_url}")

    @contextlib.contextmanager
    def _use_version(self, version: int):
        self._headers["Version"] = str(version)
        yield
        del self._headers["Version"]

    @contextlib.contextmanager
    def _use_method(self, method: str):
        self._headers["_method"] = method
        yield
        del self._headers["_method"]

    def _get_market_data(self, market_code: str) -> Tuple[Snapshot, float]:
        markets_url = self._master_url + "markets/"

        with self._use_version(3):
            r = requests.get(url=markets_url + market_code, headers=self._headers)

        assert r.status_code == 200
        reply = r.json()
        snap = Snapshot(reply["snapshot"])
        instrument_el = reply["instrument"]
        dealing_rules = reply["dealingRules"]

        assert market_code == instrument_el["epic"]
        assert instrument_el["marginFactorUnit"] == "PERCENTAGE"
        margin_req = float(instrument_el["marginFactor"]) / 100

        return snap, margin_req

    def _open_position(self, market, amount) -> str:
        otc_url = self._master_url + "positions/otc/"

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
        with self._use_version(2):
            r = requests.post(url=otc_url, headers=self._headers, json=body)
        assert r.status_code == 200, r.json()

        return r.json()["dealReference"]

    def _deal_confirm(self, deal_reference) -> Position:
        trade_confirm_url = self._master_url + "confirms/"

        r = requests.get(
            url=f"{trade_confirm_url}/{deal_reference}", headers=self._headers
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

        return Position(
            amount=amount,
            market_data=self.get_market_data(market),
            price=price,
            deal_id=deal_id,
        )
