import requests
import datetime

class PolygonClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base = "https://api.polygon.io"
    
    def fetch_snapshot(self, symbol):
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

    # def fetch_snapshot(self, symbol):
    #     """Fetch snapshot (bid, ask, last trade, orderbook depth)."""
    #     url = f"{self.base}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
    #     params = {"apiKey": self.api_key}

    #     try:
    #         response = requests.get(url, params=params)
    #         data = response.json()
    #     except Exception:
    #         return None

    #     # Validate response
    #     if data.get("status") != "OK" or "ticker" not in data:
    #         return None

    #     t = data["ticker"]

    #     # Safe extraction
    #     last_quote = t.get("lastQuote", {}) or {}
    #     last_trade = t.get("lastTrade", {}) or {}
    #     day_data = t.get("day", {}) or {}

    #     bid = last_quote.get("p")
    #     ask = last_quote.get("P")
    #     close = last_trade.get("p")
    #     volume = day_data.get("v")

    #     # Depth (Level 2)
    #     depth1 = last_quote.get("s", 0)
    #     depth2 = last_quote.get("S", 0)
    #     depth3 = depth1 + depth2

    #     # Execution price (simulate)
    #     execution_price = ask
    #     expected_price = (bid + ask) / 2 if bid and ask else None
    #     execution_time_ms = 10

    #     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #     return {
    #         "timestamp": timestamp,
    #         "bid": bid,
    #         "ask": ask,
    #         "volume": volume,
    #         "expected_price": expected_price,
    #         "execution_price": execution_price,
    #         "execution_time_ms": execution_time_ms,
    #         "depth1": depth1,
    #         "depth2": depth2,
    #         "depth3": depth3,
    #         "close": close
    #     }

    def fetch_multiple(self, companies: dict):
        """Fetch snapshot for multiple companies."""
        results = []
        for name, symbol in companies.items():
            row = self.fetch_snapshot(symbol)
            if row:
                row["company"] = name
                results.append(row)
        return results


# import requests
# import datetime

# class PolygonClient:
#     def __init__(self, api_key):
#         self.api_key = api_key
#         self.base = "https://api.polygon.io"

#     def fetch_snapshot(self, symbol):
#         """Fetch snapshot (bid, ask, last trade, orderbook depth)."""
#         url = f"{self.base}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
#         params = {"apiKey": self.api_key}

#         try:
#             response = requests.get(url, params=params)
#             data = response.json()
#         except Exception:
#             return None

#         # Validate response
#         if "ticker" not in data or data.get("status") != "OK":
#             return None

#         t = data["ticker"]

#         # Safe extraction
#         last_quote = t.get("lastQuote", {})
#         last_trade = t.get("lastTrade", {})
#         day_data = t.get("day", {})

#         bid = last_quote.get("p")
#         ask = last_quote.get("P")
#         close = last_trade.get("p")
#         volume = day_data.get("v")

#         # Depth (Level 2)
#         depth1 = last_quote.get("s", 0)
#         depth2 = last_quote.get("S", 0)
#         depth3 = depth1 + depth2  # synthetic

#         # Execution price (simulate)
#         execution_price = ask
#         expected_price = (bid + ask) / 2 if bid and ask else None
#         execution_time_ms = 10  # synthetic latency

#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         return {
#             "timestamp": timestamp,
#             "bid": bid,
#             "ask": ask,
#             "volume": volume,
#             "expected_price": expected_price,
#             "execution_price": execution_price,
#             "execution_time_ms": execution_time_ms,
#             "depth1": depth1,
#             "depth2": depth2,
#             "depth3": depth3,
#             "close": close
#         }

#     def fetch_multiple(self, companies: dict):
#         """Fetch snapshot for multiple companies."""
#         results = []
#         for name, symbol in companies.items():
#             row = self.fetch_snapshot(symbol)
#             if row:
#                 row["company"] = name
#                 results.append(row)
#         return results
