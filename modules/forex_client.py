# modules/forex_client.py

from typing import Dict, List
from modules.api_client import MarketAPI
import pandas as pd #noqa


class ForexClient:
    """
    Forex client using Binance orderbook.
    Fixes Pylance errors by converting NumPy scalars safely.
    """

    def __init__(self):
        self.api = MarketAPI("https://api.binance.com")

    def _safe_float(self, value):
        """Convert numpy/pandas scalar → Python float safely."""
        try:
            if hasattr(value, "item"):
                return float(value.item())
            return float(value)
        except Exception:
            return None

    def fetch_snapshot(self, symbol: str) -> Dict:
        bids, asks = self.api.get_orderbook(symbol)

        has_bids = bids is not None and not bids.empty
        has_asks = asks is not None and not asks.empty

        top_bid = self._safe_float(bids.iloc[0, 0]) if has_bids else None
        top_ask = self._safe_float(asks.iloc[0, 0]) if has_asks else None

        spread = (top_ask - top_bid) if (top_bid is not None and top_ask is not None) else None

        return {
            "symbol": symbol,
            "bid": top_bid,
            "ask": top_ask,
            "spread": spread,
            "timestamp": "Live FX (Binance)",
        }

    def fetch_multiple(self, pairs: Dict[str, str]) -> Dict[str, List]:
        success: List[Dict] = []
        failed: List = []

        for name, symbol in pairs.items():
            try:
                row = self.fetch_snapshot(symbol)
                row["pair"] = name
                success.append(row)
            except Exception:
                failed.append((name, symbol))

        return {"success": success, "failed": failed}


# from modules.api_client import MarketAPI

# class ForexClient:
#     def __init__(self):
#         self.api = MarketAPI("https://api.binance.com")

#     def fetch_snapshot(self, symbol: str):
#         bids, asks = self.api.get_orderbook(symbol)
#         return {
#             "symbol": symbol,
#             "bid": float(bids[0][0]) if bids else None,
#             "ask": float(asks[0][0]) if asks else None,
#             "spread": (float(asks[0][0]) - float(bids[0][0])) if bids and asks else None,
#             "timestamp": "Live FX (Binance)",
#         }

#     def fetch_multiple(self, pairs: dict):
#         success = []
#         for name, symbol in pairs.items():
#             row = self.fetch_snapshot(symbol)
#             row["pair"] = name
#             success.append(row)
#         return {"success": success, "failed": []}
