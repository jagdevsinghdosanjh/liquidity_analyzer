# modules/india_client.py

from __future__ import annotations

from typing import Dict, List, Tuple, Optional
from dhanhq import dhanhq
import datetime
import time


class IndiaClient:
    """
    Client for Indian market data using DhanHQ.

    Assumptions (you MUST align with actual DhanHQ response):
    - There is a method like `get_market_quote_full(security_id: str)` that returns
      a dict with:
        - last_traded_price
        - volume_traded
        - best_bid_price
        - best_ask_price
        - market_depth: { "bids": [...], "asks": [...] }
    - Each depth level has "price" and "quantity" fields (or similar).

    Adjust the keys below once you inspect a real response.
    """

    def __init__(self, client_id: str, access_token: str) -> None:
        self.client = dhanhq(client_id, access_token)

    # -----------------------------
    # Single snapshot fetch
    # -----------------------------
    def fetch_snapshot(self, security_id: str) -> Optional[Dict]:
        """
        Fetch snapshot + top-of-book + depth for a single Indian instrument.

        Returns a dict with keys:
        bid, ask, close, volume, depth1, depth2, depth3,
        expected_price, execution_price, execution_time_ms,
        timestamp
        or None if everything is missing.
        """
        try:
            # You may need to adjust this method name and parameters
            quote = self.client.get_market_quote_full(security_id)
        except Exception:
            return None

        if not quote:
            return None

        # ---- Extract core fields (adjust keys as per real response) ----
        bid = quote.get("best_bid_price")
        ask = quote.get("best_ask_price")
        close = quote.get("last_traded_price")
        volume = quote.get("volume_traded")

        # Depth – assuming structure:
        # quote["market_depth"]["bids"] -> list of levels with "quantity"
        # quote["market_depth"]["asks"] -> list of levels with "quantity"
        market_depth = quote.get("market_depth", {}) or {}
        bids = market_depth.get("bids", []) or []
        asks = market_depth.get("asks", []) or []

        depth1 = bids[0].get("quantity") if bids and isinstance(bids[0], dict) else 0
        depth2 = asks[0].get("quantity") if asks and isinstance(asks[0], dict) else 0

        # If absolutely nothing is there, skip this instrument
        if bid is None and ask is None and close is None and volume is None:
            return None

        # ---- Compute synthetic fields ----
        if bid is not None and ask is not None:
            expected_price = (bid + ask) / 2
        else:
            expected_price = close

        execution_price = ask if ask is not None else close
        depth3 = (depth1 or 0) + (depth2 or 0)

        row = {
            "bid": bid,
            "ask": ask,
            "close": close,
            "volume": volume,
            "depth1": depth1,
            "depth2": depth2,
            "expected_price": expected_price,
            "execution_price": execution_price,
            "execution_time_ms": 20,
            "depth3": depth3,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return row

    # -----------------------------
    # Multi-symbol fetch with retry
    # -----------------------------
    def fetch_multiple(self, companies: Dict[str, str]) -> Dict[str, List]:
        """
        Fetch snapshots for many Indian instruments.

        companies: { "Reliance Industries (RELIANCE)": "SECURITY_ID", ... }

        Returns:
            {
                "success": [row dicts with company, symbol, quality],
                "failed": [(name, symbol), ...],
            }
        """
        success: List[Dict] = []
        failed: List[Tuple[str, str]] = []

        for name, security_id in companies.items():
            row = self.fetch_snapshot(security_id)
            if row:
                row["company"] = name
                row["symbol"] = security_id
                row["quality"] = self._quality(row)
                success.append(row)
            else:
                failed.append((name, security_id))

        # Simple retry once
        if failed:
            time.sleep(2)
            retry_success: List[Dict] = []
            still_failed: List[Tuple[str, str]] = []

            for name, security_id in failed:
                row = self.fetch_snapshot(security_id)
                if row:
                    row["company"] = name
                    row["symbol"] = security_id
                    row["quality"] = self._quality(row)
                    retry_success.append(row)
                else:
                    still_failed.append((name, security_id))

            success.extend(retry_success)
            failed = still_failed

        return {"success": success, "failed": failed}

    # -----------------------------
    # Data quality tagging
    # -----------------------------
    def _quality(self, row: Dict) -> str:
        """
        Full  = bid, ask, volume all present
        Partial = close or volume present
        Missing = otherwise
        """
        if row.get("bid") is not None and row.get("ask") is not None and row.get("volume") is not None:
            return "Full"
        if row.get("close") is not None or row.get("volume") is not None:
            return "Partial"
        return "Missing"
