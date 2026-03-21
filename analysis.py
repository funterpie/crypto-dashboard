import streamlit as st
import psycopg2
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def get_db_connection():
    """Connect to the database using Streamlit secrets."""
    try:
        conn = psycopg2.connect(
            dbname=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"]
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def run_query(query):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error running query: {e}")
        return []

# Example query function
def get_top_5_gainers():
    query = """
        SELECT name, symbol, price_change_24h
        FROM crypto_market
        ORDER BY price_change_24h DESC
        LIMIT 5;
    """
    return run_query(query)

# Streamlit dashboard
st.title("Crypto Dashboard")

st.subheader("Top 5 Gainers (24h)")
top_gainers = get_top_5_gainers()
for coin in top_gainers:
    st.write(f"{coin[0]} ({coin[1]}): {coin[2]}%")