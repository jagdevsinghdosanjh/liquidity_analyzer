# modules/api_client.py

import requests
import pandas as pd
from typing import Tuple

class MarketAPI:
    """
    Generic market API client for Binance orderbook.

    - Validates HTTP status codes
    - Validates response structure
    - Raises clear errors instead of cryptic KeyError
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_orderbook(
        self,
        symbol: str = "BTCUSDT",
        limit: int = 50,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch orderbook for a given symbol from Binance-like /api/v3/depth.

        Returns:
            (bids_df, asks_df) as float-typed DataFrames with columns ["price", "qty"].

        Raises:
            RuntimeError: on HTTP or API-level errors
            KeyError: if expected keys are missing from a seemingly valid response
        """
        url = f"{self.base_url}/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}

        try:
            response = requests.get(url, params=params, timeout=10)
        except Exception as exc:
            raise RuntimeError(f"Network error while fetching orderbook for {symbol}: {exc}") from exc

        if response.status_code != 200:
            # Try to surface Binance error JSON if present
            try:
                err = response.json()
            except Exception:
                err = response.text
            raise RuntimeError(f"HTTP {response.status_code} fetching {symbol} orderbook: {err}")

        try:
            data = response.json()
        except Exception as exc:
            raise RuntimeError(f"Invalid JSON response for {symbol} orderbook: {exc}") from exc

        # Binance error payload pattern: {"code": ..., "msg": "..."}
        if isinstance(data, dict) and "code" in data and "msg" in data and "bids" not in data:
            raise RuntimeError(f"API error for {symbol}: code={data.get('code')} msg={data.get('msg')}")

        if "bids" not in data or "asks" not in data:
            raise KeyError(f"Orderbook keys missing for {symbol}. Response keys: {list(data.keys())}")

        # Construct DataFrames and ensure numeric types
        bids_raw = data.get("bids", [])
        asks_raw = data.get("asks", [])

        bids = pd.DataFrame(bids_raw, columns=["price", "qty"])
        asks = pd.DataFrame(asks_raw, columns=["price", "qty"])

        # Convert to float, row-wise if necessary to avoid silent failures
        for df in (bids, asks):
            for col in ["price", "qty"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Drop rows that failed conversion entirely
            df.dropna(subset=["price", "qty"], inplace=True)

        return bids, asks
