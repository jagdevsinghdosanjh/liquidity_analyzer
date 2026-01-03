import requests
import pandas as pd

class MarketAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_orderbook(self, symbol="BTCUSDT", limit=50):
        url = f"{self.base_url}/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}
        data = requests.get(url, params=params).json()

        bids = pd.DataFrame(data["bids"], columns=["price", "qty"]).astype(float)
        asks = pd.DataFrame(data["asks"], columns=["price", "qty"]).astype(float)

        return bids, asks
