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
# Streamlit Page Config (must be FIRST)
# -----------------------------------
st.set_page_config(page_title="Liquidity Analyzer Pro", layout="wide")
st.title("💧 Liquidity Analyzer Pro")

# -----------------------------------
# Load Secrets
# -----------------------------------
POLYGON_API_KEY = st.secrets["polygon"]["api_key"]

# -----------------------------------
# Company List
# -----------------------------------
COMPANIES = {
    "Apple Inc. (AAPL)": "AAPL",
    "Alphabet Inc. (GOOGL)": "GOOGL",
    "Microsoft Corporation (MSFT)": "MSFT",
    "NVIDIA Corporation (NVDA)": "NVDA",
    "Tesla, Inc. (TSLA)": "TSLA",
    "Infosys Ltd. (INFY)": "INFY",
    "Amazon.com, Inc. (AMZN)": "AMZN",
    "Meta Platforms, Inc. (META)": "META",
    "Intel Corporation (INTC)": "INTC",
    "Advanced Micro Devices, Inc. (AMD)": "AMD",
    "Oracle Corporation (ORCL)": "ORCL",
    "Cisco Systems, Inc. (CSCO)": "CSCO",
    "IBM Corporation (IBM)": "IBM",
    "Reliance Industries Ltd. (RELIANCE)": "RELIANCE",
    "Tata Consultancy Services Ltd. (TCS)": "TCS",
    "HCL Technologies Ltd. (HCLTECH)": "HCLTECH",
    "Wipro Ltd. (WIPRO)": "WIPRO",
    "Bharti Airtel Ltd. (BHARTIARTL)": "BHARTIARTL",
    "ICICI Bank Ltd. (ICICIBANK)": "ICICIBANK",
    "HDFC Bank Ltd. (HDFCBANK)": "HDFCBANK"
}

# -----------------------------------
# Polygon Client
# -----------------------------------
client = PolygonClient(POLYGON_API_KEY)

# -----------------------------------
# Sidebar – Polygon Fetch Button
# -----------------------------------
if st.sidebar.button("Fetch Polygon Data"):
    US_COMPANIES = {k: v for k, v in COMPANIES.items() if v.isupper() and len(v) <= 5}
    data = client.fetch_multiple(US_COMPANIES)
    st.subheader("📡 Polygon Real-Time Data")
    st.dataframe(data)

# -----------------------------------
# Initialize variables to avoid warnings
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
    st.plotly_chart(plot_volume(df), width='stretch')
    st.plotly_chart(plot_spread(df), width='stretch')

elif source == "Binance API" and bids is not None and asks is not None:
    st.plotly_chart(depth_heatmap(bids, asks), width='stretch')

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
