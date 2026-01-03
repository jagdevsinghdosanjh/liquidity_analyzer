import requests
import datetime
import time


class PolygonClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base = "https://api.polygon.io"

    # -----------------------------
    # Helper: GET request wrapper
    # -----------------------------
    def _get(self, url, params):
        try:
            r = requests.get(url, params=params, timeout=5)
            return r.json()
        except Exception:
            return None

    # -----------------------------
    # Endpoint 1: v3 Snapshot
    # -----------------------------
    def _snapshot_v3(self, symbol):
        url = f"{self.base}/v3/snapshot?ticker={symbol}"
        params = {"apiKey": self.api_key}
        data = self._get(url, params)

        if not data or "results" not in data or not data["results"]:
            return None

        r = data["results"]

        return {
            "bid": r.get("lastQuote", {}).get("bid"),
            "ask": r.get("lastQuote", {}).get("ask"),
            "close": r.get("lastTrade", {}).get("price"),
            "volume": r.get("day", {}).get("volume"),
            "depth1": r.get("lastQuote", {}).get("bidSize", 0),
            "depth2": r.get("lastQuote", {}).get("askSize", 0),
        }

    # -----------------------------
    # Endpoint 2: v2 Aggregates (Prev Day)
    # -----------------------------
    def _aggs_prev(self, symbol):
        url = f"{self.base}/v2/aggs/ticker/{symbol}/prev"
        params = {"apiKey": self.api_key}
        data = self._get(url, params)

        if not data or "results" not in data or not data["results"]:
            return None

        r = data["results"][0]

        return {
            "close": r.get("c"),
            "volume": r.get("v"),
        }

    # -----------------------------
    # Endpoint 3: Last Quote (fills bid/ask)
    # -----------------------------
    def _last_quote(self, symbol):
        url = f"{self.base}/v2/last/quote/{symbol}"
        params = {"apiKey": self.api_key}
        data = self._get(url, params)

        if not data or "results" not in data:
            return None

        r = data["results"]

        return {
            "bid": r.get("bid"),
            "ask": r.get("ask"),
        }

    # -----------------------------
    # Endpoint 4: Last Trade (fills close)
    # -----------------------------
    def _last_trade(self, symbol):
        url = f"{self.base}/v2/last/trade/{symbol}"
        params = {"apiKey": self.api_key}
        data = self._get(url, params)

        if not data or "results" not in data:
            return None

        r = data["results"]

        return {
            "close": r.get("price"),
        }

    # -----------------------------
    # Main Snapshot with Fallbacks
    # -----------------------------
    def fetch_snapshot(self, symbol):
        # 1) Try v3 snapshot
        snap = self._snapshot_v3(symbol)

        # 2) Fallback to aggregates
        aggs = self._aggs_prev(symbol)

        # 3) Fill missing bid/ask
        quote = self._last_quote(symbol)

        # 4) Fill missing close
        trade = self._last_trade(symbol)

        # Merge all data
        merged = {
            "bid": None,
            "ask": None,
            "close": None,
            "volume": None,
            "depth1": 0,
            "depth2": 0,
        }

        for src in [snap, aggs, quote, trade]:
            if src:
                merged.update({k: v for k, v in src.items() if v is not None})

        # If everything is missing → fail
        if all(v is None for v in merged.values()):
            return None

        # Compute synthetic fields
        expected_price = None
        if merged["bid"] and merged["ask"]:
            expected_price = (merged["bid"] + merged["ask"]) / 2
        else:
            expected_price = merged["close"]

        merged["expected_price"] = expected_price
        merged["execution_price"] = merged["ask"] or merged["close"]
        merged["execution_time_ms"] = 20
        merged["depth3"] = merged["depth1"] + merged["depth2"]
        merged["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return merged

    # -----------------------------
    # Multi-symbol fetch with retry
    # -----------------------------
    def fetch_multiple(self, companies: dict):
        success = []
        failed = []

        for name, symbol in companies.items():
            row = self.fetch_snapshot(symbol)

            if row:
                row["company"] = name
                row["symbol"] = symbol
                row["quality"] = self._quality(row)
                success.append(row)
            else:
                failed.append((name, symbol))

        # Retry failed once
        if failed:
            time.sleep(2)
            retry_success = []
            still_failed = []

            for name, symbol in failed:
                row = self.fetch_snapshot(symbol)
                if row:
                    row["company"] = name
                    row["symbol"] = symbol
                    row["quality"] = self._quality(row)
                    retry_success.append(row)
                else:
                    still_failed.append((name, symbol))

            success.extend(retry_success)
            failed = still_failed

        return {"success": success, "failed": failed}

    # -----------------------------
    # Data Quality Tagging
    # -----------------------------
    def _quality(self, row):
        if row["bid"] and row["ask"] and row["volume"]:
            return "Full"
        if row["close"] or row["volume"]:
            return "Partial"
        return "Missing"
