# app.py

from __future__ import annotations

import streamlit as st
import pandas as pd

from modules.polygon_client import PolygonClient
from modules.india_client import IndiaClient
from modules.forex_client import ForexClient
from modules.data_loader import load_csv
from modules.api_client import MarketAPI
from modules.liquidity_metrics import (
    bid_ask_spread,
    amihud_illiquidity,
    order_book_imbalance,
)
from modules.visualizer import plot_volume, plot_spread, depth_heatmap
from modules.report_generator import generate_report
from modules.teaching_mode import explain


# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(page_title="Liquidity Analyzer Pro", layout="wide")
st.title("💧 Liquidity Analyzer Pro")


# -----------------------------------
# Secrets
# -----------------------------------
POLYGON_API_KEY = st.secrets.get("polygon", {}).get("api_key")
DHAN_CLIENT_ID = st.secrets.get("dhan", {}).get("client_id")
DHAN_ACCESS_TOKEN = st.secrets.get("dhan", {}).get("access_token")


# -----------------------------------
# Universe definitions
# -----------------------------------

US_COMPANIES = {
    "Apple Inc. (AAPL)": "AAPL",
    "Alphabet Inc. (GOOGL)": "GOOGL",
    "Microsoft Corporation (MSFT)": "MSFT",
    "NVIDIA Corporation (NVDA)": "NVDA",
    "Tesla, Inc. (TSLA)": "TSLA",
    "Amazon.com, Inc. (AMZN)": "AMZN",
    "Meta Platforms, Inc. (META)": "META",
    "Intel Corporation (INTC)": "INTC",
    "Advanced Micro Devices, Inc. (AMD)": "AMD",
    "Oracle Corporation (ORCL)": "ORCL",
    "Cisco Systems, Inc. (CSCO)": "CSCO",
    "IBM Corporation (IBM)": "IBM",
    "Netflix, Inc. (NFLX)": "NFLX",
    "Broadcom Inc. (AVGO)": "AVGO",
    "Qualcomm Inc. (QCOM)": "QCOM",
    "Salesforce, Inc. (CRM)": "CRM",
    "PayPal Holdings, Inc. (PYPL)": "PYPL",
    "Adobe Inc. (ADBE)": "ADBE",
    "Costco Wholesale (COST)": "COST",
    "Walmart Inc. (WMT)": "WMT",
    "The Coca-Cola Company (KO)": "KO",
    "PepsiCo, Inc. (PEP)": "PEP",
    "McDonald's Corporation (MCD)": "MCD",
    "Boeing Company (BA)": "BA",
    "JPMorgan Chase & Co. (JPM)": "JPM",
    "Bank of America (BAC)": "BAC",
    "Visa Inc. (V)": "V",
    "Mastercard Inc. (MA)": "MA",
    "Exxon Mobil Corporation (XOM)": "XOM",
    "Chevron Corporation (CVX)": "CVX",
    "Pfizer Inc. (PFE)": "PFE",
    "Johnson & Johnson (JNJ)": "JNJ",
}

INDIA_COMPANIES = {
    "Reliance Industries (RELIANCE)": "RELIANCE",
    "Tata Consultancy Services (TCS)": "TCS",
    "HDFC Bank (HDFCBANK)": "HDFCBANK",
    "Infosys (INFY)": "INFY",
    "ICICI Bank (ICICIBANK)": "ICICIBANK",
    "State Bank of India (SBIN)": "SBIN",
    "Larsen & Toubro (LT)": "LT",
    "Bharti Airtel (AIRTEL)": "AIRTEL",
    "Hindustan Unilever (HINDUNILVR)": "HINDUNILVR",
    "ITC Limited (ITC)": "ITC",
    "Kotak Mahindra Bank (KOTAKBANK)": "KOTAKBANK",
    "Axis Bank (AXISBANK)": "AXISBANK",
    "Bajaj Finance (BAJFINANCE)": "BAJFINANCE",
    "Bajaj Finserv (BAJAJFINSV)": "BAJAJFINSV",
    "Maruti Suzuki (MARUTI)": "MARUTI",
    "Mahindra & Mahindra (M&M)": "M&M",
    "UltraTech Cement (ULTRACEMCO)": "ULTRACEMCO",
    "Asian Paints (ASIANPAINT)": "ASIANPAINT",
    "Titan Company (TITAN)": "TITAN",
    "Sun Pharma (SUNPHARMA)": "SUNPHARMA",
    "Wipro (WIPRO)": "WIPRO",
    "Tech Mahindra (TECHM)": "TECHM",
    "Power Grid Corporation (POWERGRID)": "POWERGRID",
    "NTPC Limited (NTPC)": "NTPC",
    "Coal India (COALINDIA)": "COALINDIA",
    "Adani Enterprises (ADANIENT)": "ADANIENT",
    "Adani Ports (ADANIPORTS)": "ADANIPORTS",
    "JSW Steel (JSWSTEEL)": "JSWSTEEL",
    "Tata Steel (TATASTEEL)": "TATASTEEL",
    "HCL Technologies (HCLTECH)": "HCLTECH",
    "Nestle India (NESTLEIND)": "NESTLEIND",
    "SBI Life Insurance (SBILIFE)": "SBILIFE",
    "HDFC Life Insurance (HDFCLIFE)": "HDFCLIFE",
    "Divi's Laboratories (DIVISLAB)": "DIVISLAB",
    "Dr. Reddy's Laboratories (DRREDDY)": "DRREDDY",
    "Eicher Motors (EICHERMOT)": "EICHERMOT",
    "Hero MotoCorp (HEROMOTOCO)": "HEROMOTOCO",
    "Tata Motors (TATAMOTORS)": "TATAMOTORS",
    "Britannia Industries (BRITANNIA)": "BRITANNIA",
    "Grasim Industries (GRASIM)": "GRASIM",
    "Havells India (HAVELLS)": "HAVELLS",
    "Zomato (ZOMATO)": "ZOMATO",
    "Paytm (PAYTM)": "PAYTM",
    "IRCTC (IRCTC)": "IRCTC",
    "Adani Green Energy (ADANIGREEN)": "ADANIGREEN",
    "Adani Total Gas (ATGL)": "ATGL",
    "Tata Power (TATAPOWER)": "TATAPOWER",
    "Tata Elxsi (TATAELXSI)": "TATAELXSI",
    "Persistent Systems (PERSISTENT)": "PERSISTENT",
    "Coforge (COFORGE)": "COFORGE",
    "Mphasis (MPHASIS)": "MPHASIS",
    "DLF Limited (DLF)": "DLF",
    "Godrej Properties (GODREJPROP)": "GODREJPROP",
    "Hindalco Industries (HINDALCO)": "HINDALCO",
    "Vedanta (VEDL)": "VEDL",
    "Bank of Baroda (BANKBARODA)": "BANKBARODA",
    "Punjab National Bank (PNB)": "PNB",
}

FOREX_PAIRS = {
    "EUR/USD (EURUSD)": "EURUSDT",
    "GBP/USD (GBPUSD)": "GBPUSDT",
    "USD/JPY (USDJPY)": "USDJPY",
    "USD/CHF (USDCHF)": "USDCHF",
    "AUD/USD (AUDUSD)": "AUDUSDT",
    "NZD/USD (NZDUSD)": "NZDUSDT",
    "USD/CAD (USDCAD)": "USDCAD",
    "EUR/GBP (EURGBP)": "EURGBP",
    "EUR/JPY (EURJPY)": "EURJPY",
    "GBP/JPY (GBPJPY)": "GBPJPY",
    "AUD/JPY (AUDJPY)": "AUDJPY",
    "CHF/JPY (CHFJPY)": "CHFJPY",
}


# -----------------------------------
# Market mode selector
# -----------------------------------
mode = st.sidebar.radio(
    "Market Mode",
    ["US Market (Polygon)", "India Market (DhanHQ)", "Forex Market (FX)"],
)


# -----------------------------------
# Client selection by mode
# -----------------------------------
if mode == "US Market (Polygon)":
    if not POLYGON_API_KEY:
        st.error("Polygon API key missing. Add it to secrets.toml or Streamlit Cloud settings.")
        st.stop()
    client = PolygonClient(POLYGON_API_KEY)
    universe = US_COMPANIES
    st.sidebar.markdown("**Mode:** US (Polygon)")

elif mode == "India Market (DhanHQ)":
    client = IndiaClient(DHAN_CLIENT_ID or "KYC_PENDING", DHAN_ACCESS_TOKEN or "KYC_PENDING")
    universe = INDIA_COMPANIES
    st.sidebar.markdown("**Mode:** India (DhanHQ – KYC Pending Placeholder)")

else:  # Forex Market (FX)
    client = ForexClient()
    universe = FOREX_PAIRS
    st.sidebar.markdown("**Mode:** Forex (Binance FX)")


# -----------------------------------
# Sidebar – Selector
# -----------------------------------
st.sidebar.subheader("Instrument Selector")
selected_name = st.sidebar.selectbox("Choose instrument", list(universe.keys()))
selected_symbol = universe[selected_name]
st.sidebar.write(f"Identifier: **{selected_symbol}**")


# -----------------------------------
# Fetch Selected
# -----------------------------------
if st.sidebar.button("Fetch Selected Instrument Data"):
    try:
        row = client.fetch_snapshot(selected_symbol)
        if row:
            st.subheader(f"📡 Real-Time Data — {selected_name}")
            df_single = pd.DataFrame([row])
            st.dataframe(df_single)
        else:
            st.warning(f"No data returned for {selected_symbol} in {mode}.")
    except Exception as exc:
        st.error(f"Error fetching snapshot for {selected_symbol}: {exc}")


# -----------------------------------
# Fetch All in universe
# -----------------------------------
if st.sidebar.button("Fetch All Instruments"):
    try:
        result = client.fetch_multiple(universe)
        success = result.get("success", [])
        failed = result.get("failed", [])

        if success:
            st.subheader(f"📡 Real-Time Data — Successful ({mode})")
            st.dataframe(pd.DataFrame(success))

        if failed:
            st.subheader("⚠️ Failed Instruments")
            for name, symbol in failed:
                st.markdown(f"- {name} (`{symbol}`)")
    except Exception as exc:
        st.error(f"Error fetching multiple instruments in {mode}: {exc}")


# -----------------------------------
# Teaching overlay
# -----------------------------------
with st.sidebar.expander("📘 Metric Guide"):
    st.markdown(
        """
        - **Bid:** Highest price buyers are willing to pay  
        - **Ask:** Lowest price sellers will accept  
        - **Spread:** Ask - Bid (tighter = more liquid)  
        - **Volume:** Total traded quantity  
        - **Depth:** Quantity at top bid/ask levels  
        - **Execution Price:** Simulated trade price  
        - **Expected Price:** Midpoint of bid and ask or last traded price  
        """
    )


# -----------------------------------
# Data source (CSV / Binance orderbook)
# -----------------------------------
st.sidebar.header("Data Source")
source = st.sidebar.radio("Choose data source", ["Upload CSV", "Binance API"])

df = None
bids = None
asks = None
metrics: dict = {}


# CSV upload
if source == "Upload CSV":
    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if file:
        df = load_csv(file)

# Binance API (generic orderbook)
elif source == "Binance API":
    api = MarketAPI("https://api.binance.com")

    default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "EURUSDT", "GBPUSDT", "AUDUSDT"]
    selected_default = st.sidebar.selectbox("Choose a default symbol", default_symbols)

    symbol_input = st.sidebar.text_input("Or enter custom symbol", value=selected_default)

    if st.sidebar.button("Fetch Binance Orderbook"):
        try:
            bids, asks = api.get_orderbook(symbol_input)
            if bids is None or bids.empty or asks is None or asks.empty:
                st.warning(f"Orderbook for {symbol_input} returned empty data.")
            else:
                st.success(f"Fetched Binance orderbook for {symbol_input}")
        except Exception as exc:
            bids, asks = None, None
            message = str(exc)

            if "451" in message or "restricted location" in message:
                st.warning(
                    "Binance orderbook data is unavailable from this region due to access restrictions."
                )
            else:
                st.error(f"Error fetching Binance orderbook for {symbol_input}: {exc}")


# -----------------------------------
# Liquidity metrics
# -----------------------------------
st.subheader("📘 Liquidity Metrics")

if source == "Upload CSV" and df is not None:
    try:
        metrics = {
            "Bid-Ask Spread": bid_ask_spread(df),
            "Amihud Illiquidity": amihud_illiquidity(df),
        }
        for name, value in metrics.items():
            st.metric(name, f"{value:.6f}")
            st.caption(explain(name))
    except Exception as exc:
        st.error(f"Error computing metrics from CSV: {exc}")

elif source == "Binance API" and bids is not None and asks is not None:
    try:
        if bids.empty or asks.empty:
            st.warning("Orderbook is empty or unavailable due to regional restrictions.")
            st.caption("Binance may block access from this region.")
        else:
            imbalance = order_book_imbalance(bids, asks)
            st.metric("Order Book Imbalance", f"{imbalance:.4f}")
            st.caption(explain("order book imbalance"))
    except Exception as exc:
        st.error(f"Error computing order book imbalance: {exc}")

else:
    st.caption("Upload a CSV or fetch a Binance orderbook to see metrics.")


# -----------------------------------
# Visualizations
# -----------------------------------
st.subheader("📊 Visualizations")

if source == "Upload CSV" and df is not None:
    try:
        st.plotly_chart(plot_volume(df), use_container_width=True)
        st.plotly_chart(plot_spread(df), use_container_width=True)
    except Exception as exc:
        st.error(f"Error generating CSV-based plots: {exc}")

elif source == "Binance API" and bids is not None and asks is not None:
    try:
        if bids.empty or asks.empty:
            st.warning("Cannot plot depth heatmap: orderbook is empty.")
        else:
            st.plotly_chart(depth_heatmap(bids, asks), use_container_width=True)
    except Exception as exc:
        st.error(f"Error generating depth heatmap: {exc}")

else:
    st.caption("Provide data above to see visualizations.")


# -----------------------------------
# PDF report
# -----------------------------------
if st.button("Generate PDF Report"):
    if metrics:
        try:
            filename = generate_report(metrics)
            st.success("Report generated!")
            with open(filename, "rb") as f:
                st.download_button("Download Report", f, file_name=filename)
        except Exception as exc:
            st.error(f"Error generating report: {exc}")
    else:
        st.warning("Metrics are not available yet. Upload a CSV first.")


# -----------------------------------
# Optional small global snapshot
# -----------------------------------
st.subheader("🌍 Global Snapshot (US / India / Forex)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**US Example (MSFT)**")
    st.caption("Use US mode above to fetch full snapshot via Polygon.")

with col2:
    st.markdown("**India Example (INFY)**")
    st.caption("India mode currently uses placeholder data (KYC pending).")

with col3:
    st.markdown("**Forex Example (EUR/USD)**")
    fx_client = ForexClient()
    try:
        fx_row = fx_client.fetch_snapshot("EURUSDT")
        spread = fx_row.get("spread")

        if spread is not None:
            st.metric("EUR/USD Spread", f"{spread:.5f}")
            st.caption("Live FX spread via Binance orderbook.")
        else:
            st.metric("EUR/USD Spread", "N/A")
            st.caption("Spread unavailable from Binance.")
    except Exception as exc:
        message = str(exc)
        if "451" in message or "restricted location" in message:
            st.metric("EUR/USD Spread", "Unavailable")
            st.caption(
                "FX data cannot be fetched from Binance in this region. "
                "This is a location restriction, not an app error."
            )
        else:
            st.metric("EUR/USD Spread", "Error")
            st.caption(f"Error fetching FX snapshot: {exc}")
