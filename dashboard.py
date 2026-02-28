import streamlit as st
import psycopg2
import logging
import pandas as pd

# Database connection details
DB_CONFIG = {
    'dbname': 'crypto_db',
    'user': 'postgres',  # Replace with your PostgreSQL username
    'password': 'taha123',  # Replace with your PostgreSQL password
    'host': 'localhost',
    'port': 5432
}

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Add a sidebar with navigation
st.sidebar.header("Crypto Dashboard Menu")
page = st.sidebar.selectbox("Select a page", ["Top 5 Gainers (24h)", "Top 5 by Market Cap", "Volatility Ranking", "Market Data", "Graphs"])

def run_query(query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error running query: {e}")
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
    top_5_gainers = run_query(get_top_5_gainers())
    gainers_data = [(coin[0], coin[1], coin[2]) for coin in top_5_gainers]
    st.table(gainers_data)

# Page 2: Top 5 by Market Cap
elif page == "Top 5 by Market Cap":
    st.title(":moneybag: Top 5 Coins by Market Cap :moneybag:")
    top_5_market_cap = run_query(get_top_5_by_market_cap())
    market_cap_data = [(coin[0], coin[1], coin[2]) for coin in top_5_market_cap]
    st.table(market_cap_data)

# Page 3: Volatility Ranking
elif page == "Volatility Ranking":
    st.title(":chart_with_upwards_trend: Volatility Ranking :chart_with_upwards_trend:")
    volatility_ranking = run_query(get_volatility_ranking())
    volatility_data = [(coin[0], coin[1], coin[2]) for coin in volatility_ranking]
    st.table(volatility_data)

# Page 4: Average Market Cap and Total Market Value
elif page == "Market Data":
    st.title(":bar_chart: Market Data :bar_chart:")
    
    # Average Market Cap
    st.header("Average Market Cap")
    avg_market_cap = run_query(get_avg_market_cap())
    st.write(f"${avg_market_cap[0][0]:,.2f}")
    
    # Total Market Value
    st.header("Total Market Value")
    total_market_value = run_query(get_total_market_value())
    st.write(f"${total_market_value[0][0]:,.2f}")

# Page 5: Graphs (Visualization)
elif page == "Graphs":
    st.title(":bar_chart: Graphs :bar_chart:")

    # Top 5 Gainers (24h) Bar Chart
    st.subheader("Top 5 Gainers (24h) Bar Chart")
    top_5_gainers = run_query(get_top_5_gainers())
    gainers_df = pd.DataFrame(top_5_gainers, columns=["Name", "Symbol", "Price Change (24h)"])
    st.bar_chart(gainers_df.set_index("Name")["Price Change (24h)"])

    # Volatility Ranking Bar Chart
    st.subheader("Volatility Ranking Bar Chart")
    volatility_ranking = run_query(get_volatility_ranking())
    volatility_df = pd.DataFrame(volatility_ranking, columns=["Name", "Symbol", "Volatility Score"])
    st.bar_chart(volatility_df.set_index("Name")["Volatility Score"])

    # Example: Total Market Value Pie Chart (Optional)
    st.subheader("Market Cap Distribution")
    top_5_market_cap = run_query(get_top_5_by_market_cap())
    market_cap_df = pd.DataFrame(top_5_market_cap, columns=["Name", "Symbol", "Market Cap"])
    st.bar_chart(market_cap_df.set_index("Name")["Market Cap"])
    
    # You can also add more charts here for different data visualizations
st.markdown("---")
st.markdown("Created with ❤️ by [Muhammad Taha Sattar Arain](https://github.com/funterpie)")