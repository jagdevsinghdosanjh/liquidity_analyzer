import requests
import datetime

class PolygonClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base = "https://api.polygon.io"

    def fetch_snapshot(self, symbol):
        """Fetch snapshot (bid, ask, last trade, orderbook depth) using Polygon v3 API."""
        url = f"{self.base}/v3/snapshot?ticker={symbol}"
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(url, params=params)
            data = response.json()
        except Exception:
            return None

        if "results" not in data or not data["results"]:
            return None

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

    def fetch_multiple(self, companies: dict):
        """Fetch snapshot for multiple companies."""
        results = []
        for name, symbol in companies.items():
            row = self.fetch_snapshot(symbol)
            if row and any(v is not None for v in row.values()):
                row["company"] = name
                results.append(row)
        return results
