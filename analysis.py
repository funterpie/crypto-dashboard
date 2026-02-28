import psycopg2
import logging
from config import DB_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def get_top_5_gainers():
    query = """
        SELECT name, symbol, price_change_24h
        FROM crypto_market
        ORDER BY price_change_24h DESC
        LIMIT 5;
    """
    return query

def get_top_5_by_market_cap():
    query = """
        SELECT name, symbol, market_cap
        FROM crypto_market
        ORDER BY market_cap DESC
        LIMIT 5;
    """
    return query

def get_avg_market_cap():
    query = """
        SELECT AVG(market_cap) AS average_market_cap
        FROM crypto_market;
    """
    return query

def get_total_market_value():
    query = """
        SELECT SUM(market_cap) AS total_market_value
        FROM crypto_market;
    """
    return query

def get_volatility_ranking():
    query = """
        SELECT name, symbol, volatility_score
        FROM crypto_market
        ORDER BY volatility_score DESC
        LIMIT 10;
    """
    return query

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

if __name__ == "__main__":
    # Top 5 Gainers (24h)
    logger.info("Fetching Top 5 Gainers (24h)...")
    top_5_gainers = run_query(get_top_5_gainers())
    for coin in top_5_gainers:
        logger.info(f"{coin[0]} ({coin[1]}): {coin[2]}%")

    # Top 5 by Market Cap
    logger.info("Fetching Top 5 by Market Cap...")
    top_5_market_cap = run_query(get_top_5_by_market_cap())
    for coin in top_5_market_cap:
        logger.info(f"{coin[0]} ({coin[1]}): {coin[2]}")

    # Average Market Cap
    logger.info("Fetching Average Market Cap...")
    avg_market_cap = run_query(get_avg_market_cap())
    logger.info(f"Average Market Cap: {avg_market_cap[0][0]}")

    # Total Market Value
    logger.info("Fetching Total Market Value...")
    total_market_value = run_query(get_total_market_value())
    logger.info(f"Total Market Value: {total_market_value[0][0]}")

    # Volatility Ranking
    logger.info("Fetching Volatility Ranking...")
    volatility_ranking = run_query(get_volatility_ranking())
    for coin in volatility_ranking:
        logger.info(f"{coin[0]} ({coin[1]}): {coin[2]}")