import psycopg2
from psycopg2 import sql
import json
import os

# Load DB config from environment (.env is supported via config.py)
from config import DB_CONFIG

def insert_data(data):
    """
    Insert transformed data into PostgreSQL using batch insert.
    """
    conn = None
    cur = None
    try:
        # Establish connection
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Create SQL statement for upsert (using ON CONFLICT)
        # plain string query works with executemany; sql.SQL not required here
        insert_query = """
            INSERT INTO crypto_market (coin_id, symbol, name, current_price, market_cap, total_volume, price_change_24h, market_cap_rank, volatility_score, extracted_at)
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

        # Prepare data for batch insert
        batch_data = [(coin['coin_id'], coin['symbol'], coin['name'], coin['current_price'],
                       coin['market_cap'], coin['total_volume'], coin['price_change_24h'],
                       coin['market_cap_rank'], coin['volatility_score'], coin['extracted_at']) for coin in data]

        # Insert data in batch
        cur.executemany(insert_query, batch_data)
        
        # Commit the transaction
        conn.commit()

        print(f"Inserted {len(data)} rows into the database.")

    except psycopg2.OperationalError as e:
        print(f"Operational error connecting to DB: {e}")
    except Exception as e:
        print(f"Error inserting data into DB: {e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

    finally:
        if cur:
            try:
                cur.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    # Load the transformed data from the JSON file
    with open('crypto_transformed.json', 'r') as f:
        transformed_data = json.load(f)
    
    # Insert the transformed data into the database
    insert_data(transformed_data)
    