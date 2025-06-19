#### Una Aplicación que
# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Yahoo Finance Stock Explorer", layout="wide")

# --- Sidebar ——————————————————————————————————————————————————————————————
st.sidebar.header("🔎 Stock & Date Filters")

# 1️⃣  Stock selector
ticker_input = st.sidebar.text_input(
    "Enter a ticker (e.g. AAPL, MSFT, TSLA):",
    value="AAPL",
    max_chars=10,
    help="Any symbol supported on finance.yahoo.com",
).upper()

# 2️⃣  Date‑range selector
today = date.today()
default_start = today - timedelta(days=365)  # last 12 months by default

start_date, end_date = st.sidebar.date_input(
    "Select date range:",
    value=(default_start, today),
    max_value=today,
)

if start_date > end_date:
    st.sidebar.error("⚠️ Start date must be ≤ end date.")
    st.stop()

# 3️⃣  Optional interval selector (daily / weekly / monthly)
interval = st.sidebar.selectbox(
    "Interval:",
    ["1d", "1wk", "1mo"],
    index=0,
    help="Granularity of historical data",
)

# --- Main body ——————————————————————————————————————————————————————————————
st.title("📈 Historical Price & Daily News")
st.write(f"**Ticker:** {ticker_input}   **Period:** {start_date} → {end_date}   **Interval:** {interval}")

# Fetch historical prices
@st.cache_data(show_spinner=False)
def load_price_data(ticker: str, start: date, end: date, interval: str) -> pd.DataFrame:
    return yf.download(
        ticker,
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),  # Yahoo data is [start, end)
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

# Fetch today’s news
@st.cache_data(show_spinner=False)
def load_today_news(ticker: str, today_: date) -> pd.DataFrame:
    tk = yf.Ticker(ticker)
    news_items = tk.news or []
    df = pd.DataFrame(news_items)
    if df.empty:
        return df
    df["datetime"] = pd.to_datetime(df["providerPublishTime"], unit="s").dt.tz_localize(None)
    df["date"] = df["datetime"].dt.date
    return df[df["date"] == today_][["datetime", "title", "link", "publisher"]].sort_values("datetime", ascending=False)

# Retrieve data
with st.status("Downloading price data…", expanded=False):
    hist = load_price_data(ticker_input, start_date, end_date, interval)

if hist.empty:
    st.error("No price data found for the specified parameters.")
    st.stop()

# Display price table & chart
st.subheader("Price Table")
st.dataframe(hist.style.format(precision=2), use_container_width=True)

st.subheader("Price Chart (Close)")
st.line_chart(hist["Close"])

# Retrieve and display today’s news
