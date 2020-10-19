from datetime import datetime, timedelta
from decimal import Decimal

import requests
import contextlib
from typing import List, Generator, Tuple, Dict

from ig_api.abstract_session import Session
from ig_api.data_model.acc_detail import AccountDetails
from ig_api.data_model.instrument import Instrument
from ig_api.data_model.market_data import MarketData
from ig_api.data_model.order import Order
from ig_api.data_model.position import Position
from ig_api.exceptions import (
    LoginError,
    MarketClosedException,
    CantOpenPosition,
    MarketNotFoundError,
    OrderNotFoundError,
)
from ig_api.data_model.snapshot import Snapshot
from loguru import logger

from ig_api import price_history_limitation

_demo_url = "https://demo-api.ig.com/gateway/deal/"


class IgSession(Session):

    UPDATE_FREQ = timedelta(minutes=3)

    def __init__(self, identifier, keys_gen, password, demo=True):
        self._master_url = _demo_url if demo else None
        self._gen_keys = keys_gen
        self._headers = {}
        self._next_key()
        self._login(identifier, password)
        self._latest_prices: Dict[str, MarketData] = {}

    def _next_key(self):
        self._headers["X-IG-API-KEY"] = next(self._gen_keys)

    def get_orders(self) -> List[Order]:
        """Get all working orders as a list. """

        orders_url = self._master_url + "workingorders"
        with self._use_version(2):
            r = requests.get(url=orders_url, headers=self._headers)

        assert r.status_code == 200, r.text
        result = []
        for wo_elem in r.json()["workingOrders"]:
            data = wo_elem["workingOrderData"]
            deal_id = data["dealId"]
            amount = data["orderSize"]
            amount = amount if data["direction"] == "BUY" else -amount
            level = data["orderLevel"]
            market_code = data["epic"]

            stop_dist = data["stopDistance"]
            limit_dist = data["limitDistance"]

            result.append(
                Order(
                    market_code=market_code,
                    amount=amount,
                    level=level,
                    stop=level - stop_dist if stop_dist else None,
                    limit=level + limit_dist if limit_dist else None,
                    deal_id=deal_id,
                )
            )
        return result

    def delete_order(self, order: Order) -> None:
        """ Delete a working order. """

        delete_order_url = self._master_url + f"workingorders/otc/{order.deal_id}"

        with self._use_version(2), self._use_method("DELETE"):
            r = requests.delete(url=delete_order_url, json={}, headers=self._headers)

        if (
            "errorCode" in r.json()
            and r.json()["errorCode"] == "error.service.delete.working.order.not.found"
        ):
            raise OrderNotFoundError(f"Order is not found on the server: {order}")
        assert r.status_code == 200, r.json()

        # deal_ref = r.json()["dealReference"]
        # reason, reply, status = self._deal_confirm(deal_ref)
        # assert status == "ACCEPTED"

    def create_order(self, market, amount, level, limit=None, stop=None) -> Order:
        """ Create a working order. """
        deal_id = self._create_order(amount, level, limit, market, stop)
        return self._deal_confirm_order(deal_id)

    def _create_order(self, amount, level, limit, market, stop):
        create_order_url = self._master_url + "workingorders/otc"
        body = {
            "epic": market,
            "expiry": "-",  # must match expiry field of market data
            "size": abs(amount),
            "level": level,
            "type": "LIMIT",
            "currencyCode": "EUR",
            "timeInForce": "GOOD_TILL_CANCELLED",
            "guaranteedStop": False,
            "direction": "BUY" if amount > 0 else "SELL",
        }
        if limit:
            body["limitLevel"] = limit
        if stop:
            body["stopLevel"] = stop
        with self._use_version(2):
            r = requests.post(url=create_order_url, headers=self._headers, json=body)
        assert r.status_code == 200, r.json()
        return r.json()["dealReference"]

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
            snap, instrument = self.market(market_code)
            price_data = MarketData.from_snapshot(snap, market_code, instrument.margin)
            self._latest_prices[market_code] = price_data

        return self._latest_prices[market_code]

    def update_market_data(self):
        now = datetime.now()
        for md in self._latest_prices.values():
            if now - md.time > self.UPDATE_FREQ:
                snap, instrument = self.market(md.market_code)
                md.update(snap)
                logger.debug(f"Updating market data: {md}.")

    def open_position(self, market: str, amount: int) -> Position:
        # TODO support limit & stop

        # TODO handle insufficient funds
        ref = self._open_position(market, amount)
        return self._deal_confirm_position(ref)

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

        assert r.status_code == 200, (r.status_code, r.text)

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
        self,
        market: str,
        resolution: str,
        start: datetime = None,
        end: datetime = None,
        n_points: int = None,
    ) -> Generator[Tuple[datetime, float, float, float], None, None]:
        """ Allows iteration over historical price data.

        Resolution must be taken from a list of supported values in Resolutions class.

        Format: iterator yields tuples (timestamp: str, low, high, spread)
        """
        prices_url = self._master_url + "prices/"
        payload = {"resolution": resolution, "pageSize": 500}

        if n_points:
            assert start is None
            assert end is None
            payload.update({"max": n_points})

        else:
            now = datetime.now()
            limit = now - price_history_limitation.limit[resolution]

            if end < limit:
                logger.info(f"Latest date with available data is {limit}.")
                return

            start = max(start, limit)
            start = start.isoformat()
            end = end.isoformat()
            payload.update({"from": start, "to": end})

        with self._use_version(3):
            r = self._request_retry_allowance(requests.get, url=prices_url + market, headers=self._headers, params=payload)
            assert r.status_code == 200, (r.status_code, r.text)

            n_pages = r.json()["metadata"]["pageData"]["totalPages"]
            init_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]

            for page in range(1, n_pages + 1):
                payload["pageNumber"] = page
                r = self._request_retry_allowance(requests.get, url=prices_url + market, headers=self._headers, params=payload)
                assert r.status_code == 200, (r.status_code, r.text)

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

                        prices = [Decimal(str(x)) for x in prices]
                        lb, la, hb, ha = prices
                        delta = ha - hb
                        low = (lb + la) / 2
                        high = (hb + ha) / 2

                        yield datetime.fromisoformat(timestamp), low, high, delta

            else:
                rem_allowance = r.json()["metadata"]["allowance"]["remainingAllowance"]
                print(
                    f"Used allowance: {init_allowance - rem_allowance}, remaining: {rem_allowance}"
                )

    def sentiment(self, market_id: str) -> float:
        """Get sentiment of a market on IG.

        Returns x, the fraction of customers holding long positions.
        Short positions can be found as 1 - x.
        """

        sentiment_url = self._master_url + f"clientsentiment/{market_id}"

        r = self._request_retry_allowance(requests.get, url=sentiment_url, headers=self._headers)
        if r.status_code != 200:
            raise LoginError(f"Failed to login: {r.text}")

        if (
            r.json()["longPositionPercentage"]
            == r.json()["shortPositionPercentage"]
            == 0.0
        ):
            raise MarketNotFoundError(
                f"Market id '{market_id}' is not valid. Use 'market details' API to find the market id."
            )

        return float(r.json()["longPositionPercentage"])/100

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

    def market(self, market_code: str) -> Tuple[Snapshot, Instrument]:
        markets_url = self._master_url + "markets/"

        with self._use_version(3):
            r = requests.get(url=markets_url + market_code, headers=self._headers)

        if r.status_code == 404 and "epic.unavailable" in r.text:
            raise MarketNotFoundError(f"Market {market_code} is not found.")

        assert r.status_code == 200, r.text
        reply = r.json()
        snap = Snapshot(reply["snapshot"])
        instrument = Instrument(reply["instrument"])
        # dealing_rules = reply["dealingRules"]

        assert market_code == instrument.epic

        return snap, instrument

    def market_navigation(self, hierarch_id=None) -> Tuple[List[int], List[str]]:
        """Get a list of hierarch_ids and list of epics under navigation node.

        For navigation root, leave hierarch_id as None."""

        nav_url = self._master_url + "marketnavigation"
        if hierarch_id is not None:
            nav_url += f"/{hierarch_id}"

        r = requests.get(url=nav_url, headers=self._headers)
        assert r.status_code == 200, r.text

        nodes = r.json()["nodes"]
        h_ids = []
        if nodes is not None:
            for el in nodes:
                h_ids.append(el["id"])

        markets = r.json()["markets"]
        epics = []
        if markets is not None:
            for el in markets:
                epics.append(el["epic"])

        return h_ids, epics

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

    def _deal_confirm_position(self, deal_reference) -> Position:
        reason, reply, status = self._deal_confirm(deal_reference)

        if status == "REJECTED":
            if "MARKET_CLOSED" in reason:
                raise MarketClosedException(
                    f"Failed to open position, the market is closed."
                )
            else:
                raise CantOpenPosition(f"Deal was rejected for reason: {reason}")

        amount, deal_id, level, market = self._confirmation_data(reply)

        return Position(
            amount=amount,
            market_data=self.get_market_data(market),
            price=level,
            deal_id=deal_id,
        )

    def _deal_confirm_order(self, deal_reference) -> Order:
        reason, reply, status = self._deal_confirm(deal_reference)
        assert status == "ACCEPTED", (status, reason)
        amount, deal_id, level, market = self._confirmation_data(reply)

        return Order(market, amount=amount, level=level, deal_id=deal_id,)

    def _confirmation_data(self, reply):
        deal_id = reply["dealId"]
        level = float(reply["level"])
        amount = int(reply["size"])
        if reply["direction"] == "SELL":
            amount *= -1
        market = reply["epic"]
        return amount, deal_id, level, market

    def _deal_confirm(self, deal_reference):
        trade_confirm_url = self._master_url + "confirms"
        r = requests.get(
            url=f"{trade_confirm_url}/{deal_reference}", headers=self._headers
        )
        assert r.status_code == 200, r.text
        reply = r.json()
        status, reason = reply["dealStatus"], reply["reason"]
        return reason, reply, status

    def _request_retry_allowance(self, callable, *args, **kwargs):
        r = callable(*args, **kwargs)
        while (
                r.text
                == '{"errorCode":"error.public-api.exceeded-account-historical-data-allowance"}'
        ):
            logger.debug(
                f"Exceeded allowance for key {self._headers['X-IG-API-KEY']}."
            )
            self._next_key()
            r = callable(*args, **kwargs)
        return r
