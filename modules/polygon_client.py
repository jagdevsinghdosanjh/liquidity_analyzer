import requests
import datetime

class PolygonClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base = "https://api.polygon.io"

    def fetch_snapshot(self, symbol):
        """Try v3 snapshot, fallback to v2 aggregates if needed."""
        url_v3 = f"{self.base}/v3/snapshot?ticker={symbol}"
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(url_v3, params=params)
            data = response.json()
        except Exception:
            return None

        if "results" in data and data["results"]:
            r = data["results"]
            bid = r.get("lastQuote", {}).get("bid")
            ask = r.get("lastQuote", {}).get("ask")
            close = r.get("lastTrade", {}).get("price")
            volume = r.get("day", {}).get("volume")
            depth1 = r.get("lastQuote", {}).get("bidSize", 0)
            depth2 = r.get("lastQuote", {}).get("askSize", 0)
            depth3 = depth1 + depth2
            expected_price = (bid + ask) / 2 if bid and ask else None
            execution_price = ask
            execution_time_ms = 10
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return {
                "timestamp": timestamp,
                "bid": bid,
                "ask": ask,
                "volume": volume,
                "expected_price": expected_price,
                "execution_price": execution_price,
                "execution_time_ms": execution_time_ms,
                "depth1": depth1,
                "depth2": depth2,
                "depth3": depth3,
                "close": close
            }

        # Fallback to v2 aggregates
        url_v2 = f"{self.base}/v2/aggs/ticker/{symbol}/prev"
        try:
            response = requests.get(url_v2, params=params)
            data = response.json()
        except Exception:
            return None

        if "results" not in data or not data["results"]:
            return None

        r = data["results"][0]
        bid = None
        ask = None
        close = r.get("c")
        volume = r.get("v")
        expected_price = close
        execution_price = close
        execution_time_ms = 20
        depth1 = 0
        depth2 = 0
        depth3 = 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "timestamp": timestamp,
            "bid": bid,
            "ask": ask,
            "volume": volume,
            "expected_price": expected_price,
            "execution_price": execution_price,
            "execution_time_ms": execution_time_ms,
            "depth1": depth1,
            "depth2": depth2,
            "depth3": depth3,
            "close": close
        }

    def fetch_multiple(self, companies: dict):
        """Fetch snapshot for multiple companies with diagnostics."""
        results = []
        failed = []

        for name, symbol in companies.items():
            row = self.fetch_snapshot(symbol)
            if row and any(v is not None for v in row.values()):
                row["company"] = name
                results.append(row)
            else:
                failed.append((name, symbol))

        return {
            "success": results,
            "failed": failed
        }
