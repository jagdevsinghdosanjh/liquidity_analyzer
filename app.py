import streamlit as st

# -----------------------------------
# Imports
# -----------------------------------
from modules.data_loader import load_csv
from modules.api_client import MarketAPI
from modules.report_generator import generate_report
from modules.teaching_mode import explain
from modules.polygon_client import PolygonClient

from modules.liquidity_metrics import (
    bid_ask_spread,
    amihud_illiquidity,
    order_book_imbalance
)

from modules.visualizer import (
    plot_volume,
    plot_spread,
    depth_heatmap
)

# -----------------------------------
# Streamlit Page Config
# -----------------------------------
st.set_page_config(page_title="Liquidity Analyzer Pro", layout="wide")
st.title("💧 Liquidity Analyzer Pro")

# -----------------------------------
# Load Secrets
# -----------------------------------
POLYGON_API_KEY = st.secrets["polygon"]["api_key"]
try:
    POLYGON_API_KEY = st.secrets["polygon"]["api_key"]
except KeyError:
    st.error("Polygon API key not found. Please add it to secrets.toml or Streamlit Cloud settings.")
    st.stop()

# -----------------------------------
# Company List
# -----------------------------------
COMPANIES = {
    "Apple Inc. (AAPL)": "AAPL",
    "Alphabet Inc. (GOOGL)": "GOOGL",
    "Microsoft Corporation (MSFT)": "MSFT",
    "NVIDIA Corporation (NVDA)": "NVDA",
    "Tesla, Inc. (TSLA)": "TSLA",
    "Infosys Ltd. (INFY)": "INFY",  # US ADR supported
    "Amazon.com, Inc. (AMZN)": "AMZN",
    "Meta Platforms, Inc. (META)": "META",
    "Intel Corporation (INTC)": "INTC",
    "Advanced Micro Devices, Inc. (AMD)": "AMD",
    "Oracle Corporation (ORCL)": "ORCL",
    "Cisco Systems, Inc. (CSCO)": "CSCO",
    "IBM Corporation (IBM)": "IBM",
}

# -----------------------------------
# Polygon Client
# -----------------------------------
client = PolygonClient(POLYGON_API_KEY)

# -----------------------------------
# Sidebar – Company Selector
# -----------------------------------
st.sidebar.subheader("Polygon Company Selector")
selected_company = st.sidebar.selectbox("Choose a company", list(COMPANIES.keys()))
selected_symbol = COMPANIES[selected_company]
st.sidebar.write(f"Symbol: **{selected_symbol}**")

# -----------------------------------
# Sidebar – Fetch Buttons
# -----------------------------------
if st.sidebar.button("Fetch Selected Company Data"):
    row = client.fetch_snapshot(selected_symbol)
    if row:
        st.subheader(f"📡 Polygon Real-Time Data — {selected_company}")
        st.dataframe([row])
    else:
        st.warning(f"No data returned for {selected_symbol}.")

# if st.sidebar.button("Fetch All Companies"):
#     data = client.fetch_multiple(COMPANIES)
#     st.subheader("📡 Polygon Real-Time Data — All Companies")
#     st.dataframe(data)
if st.sidebar.button("Fetch All Companies"):
    result = client.fetch_multiple(COMPANIES)
    success = result["success"]
    failed = result["failed"]

    if success:
        st.subheader("📡 Polygon Real-Time Data — Successful")
        st.dataframe(success)
    else:
        st.warning("No successful data returned.")

    if failed:
        st.subheader("⚠️ Failed Symbols")
        for name, symbol in failed:
            st.markdown(f"- {name} (`{symbol}`)")

# -----------------------------------
# Initialize variables
# -----------------------------------
df = None
bids = None
asks = None
metrics = {}

# -----------------------------------
# Sidebar – Data Source
# -----------------------------------
st.sidebar.header("Data Source")
source = st.sidebar.radio("Choose data source", ["Upload CSV", "Binance API"])

# -----------------------------------
# CSV Upload Mode
# -----------------------------------
if source == "Upload CSV":
    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if file:
        df = load_csv(file)

# -----------------------------------
# Binance API Mode
# -----------------------------------
elif source == "Binance API":
    api = MarketAPI("https://api.binance.com")
    symbol = st.sidebar.text_input("Symbol", "BTCUSDT")
    bids, asks = api.get_orderbook(symbol)

# -----------------------------------
# Metrics Section
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
# PDF Report
# -----------------------------------
if st.button("Generate PDF Report"):
    if metrics:
        filename = generate_report(metrics)
        st.success("Report generated!")
        with open(filename, "rb") as f:
            st.download_button("Download Report", f, file_name=filename)
    else:
        st.warning("Metrics are not available yet. Upload a CSV first.")
