# app.py

from __future__ import annotations

import streamlit as st
import pandas as pd

from modules.polygon_client import PolygonClient
from modules.india_client import IndiaClient
from modules.data_loader import load_csv
from modules.api_client import MarketAPI
from modules.liquidity_metrics import bid_ask_spread, amihud_illiquidity, order_book_imbalance
from modules.visualizer import plot_volume, plot_spread, depth_heatmap
from modules.report_generator import generate_report
from modules.teaching_mode import explain


# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(page_title="Liquidity Dual Analyzer Pro", layout="wide")
st.title("💧 Liquidity Dual Analyzer Pro")


# -----------------------------------
# Secrets
# -----------------------------------
# Polygon (US)
POLYGON_API_KEY = st.secrets.get("polygon", {}).get("api_key")

# Dhan (India)
DHAN_CLIENT_ID = st.secrets.get("dhan", {}).get("client_id")
DHAN_ACCESS_TOKEN = st.secrets.get("dhan", {}).get("access_token")


# -----------------------------------
# Company lists
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

    # --- Additional High-Liquidity US Stocks ---
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
FOREX_PAIRS = {
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "USD/JPY": "USDJPY",
    "USD/CHF": "USDCHF",
    "AUD/USD": "AUDUSD",
    "NZD/USD": "NZDUSD",
    "USD/CAD": "USDCAD",

    # Cross pairs
    "EUR/GBP": "EURGBP",
    "EUR/JPY": "EURJPY",
    "GBP/JPY": "GBPJPY",
    "AUD/JPY": "AUDJPY",
    "CHF/JPY": "CHFJPY",
}

INDIA_COMPANIES = {
    # --- Your Original Entries ---
    "Reliance Industries (RELIANCE)": "RELIANCE",
    "Tata Consultancy Services (TCS)": "TCS",
    "HDFC Bank (HDFCBANK)": "HDFCBANK",
    "Infosys (INFY)": "INFY",
    "ICICI Bank (ICICIBANK)": "ICICIBANK",
    "State Bank of India (SBIN)": "SBIN",
    "Larsen & Toubro (LT)": "LT",
    "Bharti Airtel (AIRTEL)": "AIRTEL",

    # --- NIFTY 50 HEAVYWEIGHTS ---
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

    # --- HIGH-LIQUIDITY MIDCAPS (Great for teaching) ---
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


# NOTE: Replace the values with Dhan's security IDs or symbols

# INDIA_COMPANIES = {
#     "Reliance Industries (RELIANCE)": "RELIANCE",
#     "Tata Consultancy Services (TCS)": "TCS",
#     "HDFC Bank (HDFCBANK)": "HDFCBANK",
#     "Infosys (INFY)": "INFY",
#     "ICICI Bank (ICICIBANK)": "ICICIBANK",
#     "State Bank of India (SBIN)": "SBIN",
#     "Larsen & Toubro (LT)": "LT",
#     "Bharti Airtel (AIRTEL)": "AIRTEL",

#     # --- Additional Large-Cap Indian Companies ---
#     "Hindustan Unilever (HINDUNILVR)": "HINDUNILVR",
#     "ITC Limited (ITC)": "ITC",
#     "Kotak Mahindra Bank (KOTAKBANK)": "KOTAKBANK",
#     "Axis Bank (AXISBANK)": "AXISBANK",
#     "Bajaj Finance (BAJFINANCE)": "BAJFINANCE",
#     "Bajaj Finserv (BAJAJFINSV)": "BAJAJFINSV",
#     "Maruti Suzuki (MARUTI)": "MARUTI",
#     "Mahindra & Mahindra (M&M)": "M&M",
#     "UltraTech Cement (ULTRACEMCO)": "ULTRACEMCO",
#     "Asian Paints (ASIANPAINT)": "ASIANPAINT",
#     "Titan Company (TITAN)": "TITAN",
#     "Sun Pharma (SUNPHARMA)": "SUNPHARMA",
#     "Wipro (WIPRO)": "WIPRO",
#     "Tech Mahindra (TECHM)": "TECHM",
#     "Power Grid Corporation (POWERGRID)": "POWERGRID",
#     "NTPC Limited (NTPC)": "NTPC",
#     "Coal India (COALINDIA)": "COALINDIA",
#     "Adani Enterprises (ADANIENT)": "ADANIENT",
#     "Adani Ports (ADANIPORTS)": "ADANIPORTS",
#     "JSW Steel (JSWSTEEL)": "JSWSTEEL",
#     "Tata Steel (TATASTEEL)": "TATASTEEL",
#     "HCL Technologies (HCLTECH)": "HCLTECH",
#     "Nestle India (NESTLEIND)": "NESTLEIND",
#     "SBI Life Insurance (SBILIFE)": "SBILIFE",
#     "HDFC Life Insurance (HDFCLIFE)": "HDFCLIFE",
#     "Divi's Laboratories (DIVISLAB)": "DIVISLAB",
#     "Dr. Reddy's Laboratories (DRREDDY)": "DRREDDY",
#     "Eicher Motors (EICHERMOT)": "EICHERMOT",
#     "Hero MotoCorp (HEROMOTOCO)": "HEROMOTOCO",
#     "Tata Motors (TATAMOTORS)": "TATAMOTORS",
#     "Britannia Industries (BRITANNIA)": "BRITANNIA",
#     "Grasim Industries (GRASIM)": "GRASIM",
#     "Havells India (HAVELLS)": "HAVELLS",
# }


# -----------------------------------
# Market mode selector
# -----------------------------------
# mode = st.sidebar.radio("Market Mode", ["US Market (Polygon)", "India Market (DhanHQ)"])
mode = st.sidebar.radio(
    "Market Mode",
    ["US Market (Polygon)", "India Market (DhanHQ)", "Forex Market (FX)"],
)

if mode == "US Market (Polygon)":
    if not POLYGON_API_KEY:
        st.error("Polygon API key missing. Add it to secrets.toml or Streamlit Cloud settings.")
        st.stop()
    client = PolygonClient(POLYGON_API_KEY)
    companies = US_COMPANIES
    st.sidebar.markdown("**Mode:** US (Polygon)")

elif mode == "India Market (DhanHQ)":
    # Using your placeholder IndiaClient for now
    if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
        # Even if missing, we can still use placeholder client
        from modules.india_client import IndiaClient
        client = IndiaClient("KYC_PENDING", "KYC_PENDING")
    else:
        from modules.india_client import IndiaClient
        client = IndiaClient(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)

    companies = INDIA_COMPANIES
    st.sidebar.markdown("**Mode:** India (DhanHQ, KYC pending)")

else:  # Forex Market (FX)
    from modules.forex_client import ForexClient

    client = ForexClient()
    companies = FOREX_PAIRS
    st.sidebar.markdown("**Mode:** Forex (Binance FX)")


# if mode == "US Market (Polygon)":
#     if not POLYGON_API_KEY:
#         st.error("Polygon API key missing. Add it to secrets.toml or Streamlit Cloud settings.")
#         st.stop()
#     client = PolygonClient(POLYGON_API_KEY)
#     companies = US_COMPANIES
#     st.sidebar.markdown("**Mode:** US (Polygon)")
# else:
#     if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
#         st.error("Dhan API credentials missing. Add them to secrets.toml or Streamlit Cloud settings.")
#         st.stop()
#     client = IndiaClient(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
#     companies = INDIA_COMPANIES
#     st.sidebar.markdown("**Mode:** India (DhanHQ)")


# -----------------------------------
# Sidebar – Company selector
# -----------------------------------
st.sidebar.subheader("Company Selector")
selected_company = st.sidebar.selectbox("Choose a company", list(companies.keys()))
selected_symbol = companies[selected_company]
st.sidebar.write(f"Identifier: **{selected_symbol}**")


# -----------------------------------
# Fetch selected company
# -----------------------------------
if st.sidebar.button("Fetch Selected Company Data"):
    row = client.fetch_snapshot(selected_symbol)
    if row:
        st.subheader(f"📡 Real-Time Data — {selected_company}")
        df_single = pd.DataFrame([row])
        st.dataframe(df_single)
    else:
        st.warning(f"No data returned for {selected_symbol} in {mode}.")


# -----------------------------------
# Fetch all companies
# -----------------------------------
if st.sidebar.button("Fetch All Companies"):
    result = client.fetch_multiple(companies)
    success = result["success"]
    failed = result["failed"]

    if success:
        st.subheader(f"📡 Real-Time Data — Successful ({mode})")
        st.dataframe(pd.DataFrame(success))

    if failed:
        st.subheader("⚠️ Failed Symbols")
        for name, symbol in failed:
            st.markdown(f"- {name} (`{symbol}`)")


# -----------------------------------
# Teaching overlay
# -----------------------------------
with st.sidebar.expander("📘 Metric Guide"):
    st.markdown(
        """
        - **Bid:** Highest price buyers are willing to pay  
        - **Ask:** Lowest price sellers will accept  
        - **Spread:** Ask - Bid (tight = liquid)  
        - **Volume:** Total traded quantity  
        - **Depth:** Quantity at top bid/ask levels  
        - **Execution Price:** Simulated trade price  
        - **Expected Price:** Midpoint of bid and ask or last traded price  
        """
    )


# -----------------------------------
# Data source (for CSV / Binance)
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

# Binance API
elif source == "Binance API":
    api = MarketAPI("https://api.binance.com")
    symbol = st.sidebar.text_input("Symbol", "BTCUSDT")
    bids, asks = api.get_orderbook(symbol)


# -----------------------------------
# Liquidity metrics
# -----------------------------------
st.subheader("📘 Liquidity Metrics")

if source == "Upload CSV" and df is not None:
    metrics = {
        "Bid-Ask Spread": bid_ask_spread(df),
        "Amihud Illiquidity": amihud_illiquidity(df),
    }

    for k, v in metrics.items():
        st.metric(k, f"{v:.6f}")
        st.caption(explain(k))

elif source == "Binance API" and bids is not None and asks is not None:
    imbalance = order_book_imbalance(bids, asks)
    st.metric("Order Book Imbalance", f"{imbalance:.4f}")
    st.caption(explain("order book imbalance"))


# -----------------------------------
# Visualizations
# -----------------------------------
st.subheader("📊 Visualizations")

if source == "Upload CSV" and df is not None:
    st.plotly_chart(plot_volume(df), use_container_width=True)
    st.plotly_chart(plot_spread(df), use_container_width=True)

elif source == "Binance API" and bids is not None and asks is not None:
    st.plotly_chart(depth_heatmap(bids, asks), use_container_width=True)


# -----------------------------------
# PDF report
# -----------------------------------
if st.button("Generate PDF Report"):
    if metrics:
        filename = generate_report(metrics)
        st.success("Report generated!")
        with open(filename, "rb") as f:
            st.download_button("Download Report", f, file_name=filename)
    else:
        st.warning("Metrics are not available yet. Upload a CSV first.")
