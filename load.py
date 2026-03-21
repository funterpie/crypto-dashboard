import psycopg2
import json
from psycopg2 import sql
from psycopg2 import pool
import logging
from config import DB_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Create a connection pool for efficiency
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    dbname=DB_CONFIG["dbname"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],  # remove https:// if you have it
    port=DB_CONFIG["port"]
)

def insert_data(data):
    """
    Insert transformed data into PostgreSQL using batch insert with upsert.
    """
    conn = None
    cur = None
    try:
        conn = db_pool.getconn()
        cur = conn.cursor()

        # Ensure table exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS crypto_market (
            coin_id TEXT PRIMARY KEY,
            symbol TEXT,
            name TEXT,
            current_price NUMERIC,
            market_cap NUMERIC,
            total_volume NUMERIC,
            price_change_24h NUMERIC,
            market_cap_rank INTEGER,
            volatility_score NUMERIC,
            extracted_at TIMESTAMP
        );
        """
        cur.execute(create_table_query)

        # Batch insert with upsert
        insert_query = """
            INSERT INTO crypto_market 
                (coin_id, symbol, name, current_price, market_cap, total_volume, price_change_24h, market_cap_rank, volatility_score, extracted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (coin_id)
            DO UPDATE SET
                current_price = EXCLUDED.current_price,
                market_cap = EXCLUDED.market_cap,
                total_volume = EXCLUDED.total_volume,
                price_change_24h = EXCLUDED.price_change_24h,
                market_cap_rank = EXCLUDED.market_cap_rank,
                volatility_score = EXCLUDED.volatility_score,
                extracted_at = EXCLUDED.extracted_at;
        """

        batch_data = [
            (
                coin['coin_id'], coin['symbol'], coin['name'], coin['current_price'],
                coin['market_cap'], coin['total_volume'], coin['price_change_24h'],
                coin['market_cap_rank'], coin['volatility_score'], coin['extracted_at']
            ) for coin in data
        ]

        cur.executemany(insert_query, batch_data)
        conn.commit()
        logger.info(f"Inserted/Updated {len(data)} rows successfully.")

    except psycopg2.OperationalError as e:
        logger.error(f"Operational error connecting to DB: {e}")
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
    finally:
        if cur:
            cur.close()
        if conn:
            db_pool.putconn(conn)

if __name__ == "__main__":
    # Load transformed data
    with open('crypto_transformed.json', 'r') as f:
        transformed_data = json.load(f)

    insert_data(transformed_data)