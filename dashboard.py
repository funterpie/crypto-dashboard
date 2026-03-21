import os
import sys
import time

import streamlit as st
import psycopg2
import logging
import pandas as pd

# altair is used for interactive charts; fall back if not available
try:
    import altair as alt
except ImportError:
    alt = None

# make the page look nicer and set a default layout
st.set_page_config(page_title="Crypto Dashboard", layout="wide", page_icon="📈")

# Ensure project root is on sys.path so `from config import ...` works under Streamlit
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import DB_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# simple caching for database results so UI stays snappy for a short while
# Streamlit will automatically invalidate the cache after ttl seconds
@st.cache_data(ttl=5)
def cached_query(query: str):
    """Run a SQL query and cache the results for a few minutes."""
    return run_query(query)

# Add a sidebar with navigation and a refresh button
st.sidebar.header("Crypto Dashboard Menu")
page = st.sidebar.selectbox("Select a page", [
    "Top 5 Gainers (24h)",
    "Top 5 by Market Cap",
    "Volatility Ranking",
    "Market Data",
    "Graphs",
    "ETL Status"
])

# manual refresh button, occasionally users want the very latest data
if st.sidebar.button("🔄 Refresh now"):
    # clear cached queries so reload pulls fresh rows
    st.cache_data.clear()
    st.rerun()

# automatically reload every 5 seconds using session state timer
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
elif time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()

def run_query(query):
    """Execute a query with a spinner + optional progress bar.

    This helper is intentionally lightweight; if called through
    ``cached_query`` the results will be memoized for a few minutes.
    """
    # show a spinner while the query is executing so users know something
    with st.spinner("Fetching data from the database..."):
        try:
            conn = psycopg2.connect(connect_timeout=5, **DB_CONFIG)
            cur = conn.cursor()
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error running query: {e}")
            try:
                st.error(f"Database error: {e}")
            except Exception:
                pass
            return []

# Function to get the Top 5 Gainers (24h)
def get_top_5_gainers():
    query = """
        SELECT name, symbol, price_change_24h
        FROM crypto_market
        ORDER BY price_change_24h DESC
        LIMIT 5;
    """
    return query

# Function to get the Top 5 by Market Cap
def get_top_5_by_market_cap():
    query = """
        SELECT name, symbol, market_cap
        FROM crypto_market
        ORDER BY market_cap DESC
        LIMIT 5;
    """
    return query

# Function to get the volatility ranking
def get_volatility_ranking():
    query = """
        SELECT name, symbol, volatility_score
        FROM crypto_market
        ORDER BY volatility_score DESC
        LIMIT 10;
    """
    return query

# Function to get the latest extraction timestamp (used for "last updated" indicator)
def get_last_update():
    query = """
        SELECT MAX(extracted_at)
        FROM crypto_market;
    """
    return query

# Function to get the average market cap
def get_avg_market_cap():
    query = """
        SELECT AVG(market_cap) AS average_market_cap
        FROM crypto_market;
    """
    return query

# Function to get the total market value
def get_total_market_value():
    query = """
        SELECT SUM(market_cap) AS total_market_value
        FROM crypto_market;
    """
    return query

# Page 1: Top 5 Gainers (24h)
if page == "Top 5 Gainers (24h)":
    st.title(":star: Top 5 Gainers (24h) :star:")
    # display last update time above the table
    last = cached_query(get_last_update())
    if last and last[0] and last[0][0]:
        st.markdown(f"**Last updated:** {last[0][0]}")

    gainers = cached_query(get_top_5_gainers())
    df_gainers = pd.DataFrame(gainers, columns=["Name", "Symbol", "Price Change (24h)"])
    st.dataframe(
        df_gainers,
        column_config={
            "Name": st.column_config.TextColumn("Coin Name"),
            "Symbol": st.column_config.TextColumn("Symbol"),
            "Price Change (24h)": st.column_config.NumberColumn(
                "24h Change (%)",
                format="%.2f %%"
            )
        },
        hide_index=True,
        width="stretch"
    )

# Page 2: Top 5 by Market Cap
elif page == "Top 5 by Market Cap":
    st.title(":moneybag: Top 5 Coins by Market Cap :moneybag:")
    last = cached_query(get_last_update())
    if last and last[0] and last[0][0]:
        st.markdown(f"**Last updated:** {last[0][0]}")

    market = cached_query(get_top_5_by_market_cap())
    df_market = pd.DataFrame(market, columns=["Name", "Symbol", "Market Cap"])
    st.dataframe(
        df_market,
        column_config={
            "Name": st.column_config.TextColumn("Coin Name"),
            "Symbol": st.column_config.TextColumn("Symbol"),
            "Market Cap": st.column_config.NumberColumn(
                "Market Cap (USD)",
                format="$%d"
            )
        },
        hide_index=True,
        width="stretch"
    )

# Page 3: Volatility Ranking
elif page == "Volatility Ranking":
    st.title(":chart_with_upwards_trend: Volatility Ranking :chart_with_upwards_trend:")
    last = cached_query(get_last_update())
    if last and last[0] and last[0][0]:
        st.markdown(f"**Last updated:** {last[0][0]}")

    volatility = cached_query(get_volatility_ranking())
    df_vol = pd.DataFrame(volatility, columns=["Name", "Symbol", "Volatility Score"])
    st.dataframe(
        df_vol,
        column_config={
            "Name": st.column_config.TextColumn("Coin Name"),
            "Symbol": st.column_config.TextColumn("Symbol"),
            "Volatility Score": st.column_config.NumberColumn(
                "Volatility Score",
                format="%.2f"
            )
        },
        hide_index=True,
        width="stretch"
    )

# Page 4: Average Market Cap and Total Market Value
elif page == "Market Data":
    st.title(":bar_chart: Market Data :bar_chart:")
    last = cached_query(get_last_update())
    if last and last[0] and last[0][0]:
        st.markdown(f"**Last updated:** {last[0][0]}")

    # display key market numbers side-by-side
    avg_market_cap = cached_query(get_avg_market_cap())
    total_market_value = cached_query(get_total_market_value())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Market Cap")
        if avg_market_cap and avg_market_cap[0] and avg_market_cap[0][0] is not None:
            st.metric("Avg Cap", f"${avg_market_cap[0][0]:,.2f}")
        else:
            st.write("No data available")
    with col2:
        st.subheader("Total Market Value")
        if total_market_value and total_market_value[0] and total_market_value[0][0] is not None:
            st.metric("Total Value", f"${total_market_value[0][0]:,.2f}")
        else:
            st.write("No data available")
            
    st.markdown("### All Monitored Coins")
    all_coins_query = "SELECT name, symbol, current_price, market_cap, total_volume, price_change_24h FROM crypto_market ORDER BY market_cap DESC;"
    all_coins = cached_query(all_coins_query)
    
    if all_coins:
        df_all = pd.DataFrame(all_coins, columns=["Name", "Symbol", "Price", "Market Cap", "Volume", "24h Change"])
        st.dataframe(
            df_all,
            column_config={
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Market Cap": st.column_config.NumberColumn("Market Cap", format="$%d"),
                "Volume": st.column_config.NumberColumn("Volume", format="$%d"),
                "24h Change": st.column_config.NumberColumn("24h Change (%)", format="%.2f%%")
            },
            hide_index=True,
            width="stretch"
        )

# Page 5: Graphs (Visualization)
elif page == "Graphs":
    st.title(":bar_chart: Market Graphs & Visualization :bar_chart:")
    last = cached_query(get_last_update())
    if last and last[0] and last[0][0]:
        st.markdown(f"**Last updated:** {last[0][0]}")
        
    st.subheader("Interactive Metrics")
    col1, col2 = st.columns([1, 2])

    with col1:
        # interactive selector to choose metric and number of coins
        metric_choice = st.selectbox(
            "Metric to display",
            ["Price Change (24h)", "Volatility Score", "Market Cap"]
        )
        limit = st.slider("Number of coins", min_value=5, max_value=20, value=5, step=1)

        # map human label to column name
        col_map = {
            "Price Change (24h)": ("price_change_24h", "Price Change (24h)"),
            "Volatility Score": ("volatility_score", "Volatility Score"),
            "Market Cap": ("market_cap", "Market Cap"),
        }
        col_key, col_label = col_map[metric_choice]

    with col2:
        query = f"SELECT name, symbol, {col_key} FROM crypto_market ORDER BY {col_key} DESC LIMIT {limit};"
        data = cached_query(query)
        if data:
            df = pd.DataFrame(data, columns=["Name", "Symbol", col_label])
            if alt is not None:
                # Colorful Bar Chart
                bar_chart = alt.Chart(df).mark_bar(cornerRadiusEnd=6).encode(
                    x=alt.X(col_label, title=col_label),
                    y=alt.Y("Name", sort="-x", title=""),
                    color=alt.Color(col_label, scale=alt.Scale(scheme='viridis'), legend=None),
                    tooltip=["Name", "Symbol", col_label]
                ).properties(title=f"Top {limit} by {col_label}")
                st.altair_chart(bar_chart, width="stretch")
            else:
                st.bar_chart(df.set_index("Name")[col_label])
        else:
            st.warning("No data available for selected metric.")

    st.markdown("---")
    st.subheader("Market Cap Distribution & 24h Trends")
    # Fetch top 10 for donut chart & scatter plot
    query_top = "SELECT name, symbol, market_cap, price_change_24h, total_volume FROM crypto_market ORDER BY market_cap DESC LIMIT 15;"
    data_top = cached_query(query_top)
    
    if data_top and alt is not None:
        df_top = pd.DataFrame(data_top, columns=["Name", "Symbol", "Market Cap", "Price Change (24h)", "Total Volume"])
        
        col3, col4 = st.columns(2)
        with col3:
            # Donut Chart for Market Cap
            donut = alt.Chart(df_top).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Market Cap", type="quantitative"),
                color=alt.Color(field="Name", type="nominal", scale=alt.Scale(scheme='category20b')),
                tooltip=["Name", "Symbol", "Market Cap"]
            ).properties(title="Market Cap Share (Top 15)", height=400)
            st.altair_chart(donut, width="stretch")
            
        with col4:
            # Scatter Plot for 24h Change vs Total Volume
            scatter = alt.Chart(df_top).mark_circle(size=200, opacity=0.8).encode(
                x=alt.X("Total Volume", title="Total Volume (USD)"),
                y=alt.Y("Price Change (24h)", title="24h Change (%)"),
                color=alt.Color("Price Change (24h)", scale=alt.Scale(scheme='redyellowgreen')),
                tooltip=["Name", "Symbol", "Price Change (24h)", "Total Volume", "Market Cap"]
            ).properties(title="Volume vs. Price Change (Top 15)", height=400)
            st.altair_chart(scatter, width="stretch")
    elif data_top:
         st.info("Install altair for advanced charts.")
    else:
         st.warning("Not enough data for advanced charts.")

# Page 6: ETL Status
elif page == "ETL Status":
    st.title(":gear: ETL Pipeline Status")
    # allow manual refresh of the status table
    if st.button("Refresh ETL status"):
        st.rerun()
    # auto‑refresh every 5 seconds using session state timestamp
    if "etl_last_refresh" not in st.session_state:
        st.session_state.etl_last_refresh = time.time()
    elif time.time() - st.session_state.etl_last_refresh > 5:
        st.session_state.etl_last_refresh = time.time()
        st.rerun()

    # retrieve the last few rows from the log table
    log_query = "SELECT run_time, status, message FROM etl_log ORDER BY run_time DESC LIMIT 20;"
    logs = run_query(log_query)  # bypass cache to get real-time status
    if logs:
        df = pd.DataFrame(logs, columns=["Time", "Status", "Message"])
        st.dataframe(df, hide_index=True, width="stretch")

        # inspect latest entry to show progress bar
        latest_status = logs[0][1]  # second column is status
        progress_map = {
            "extracting": 0.2,
            "extracted": 0.3,
            "transforming": 0.5,
            "transformed": 0.6,
            "loading": 0.8,
            "loaded": 0.9,
            "completed": 1.0,
        }
        if latest_status in progress_map and progress_map[latest_status] < 1.0:
            st.info(f"ETL currently: {latest_status}")
            pb = st.progress(progress_map[latest_status])
        elif latest_status == "completed":
            st.success("Last run finished successfully")
        elif latest_status == "error":
            st.error("Last run ended in error – check the message above")
    else:
        st.write("No ETL runs recorded yet.")
st.markdown("---")
st.markdown("Created with ❤️ by [Muhammad Taha Sattar Arain](https://github.com/funterpie)")

# inform user about caching & refresh behavior
st.caption("Data is pulled from the database and the page automatically refreshes every 5 seconds")