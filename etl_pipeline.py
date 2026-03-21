import os
import sys
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from psycopg2 import pool, OperationalError
from extract import extract_crypto_data
from transform import transform_data
from load import insert_data

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import DB_CONFIG

# ----------------- Logging Setup -----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# ----------------- Connection Pool -----------------
try:
    db_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )
    if db_pool:
        logger.info("Connection pool created successfully")
except OperationalError as e:
    logger.error(f"Failed to create connection pool: {e}")
    sys.exit(1)

# ----------------- ETL Log Function -----------------
def log_etl(status, message=None):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS etl_log (
                run_id SERIAL PRIMARY KEY,
                run_time TIMESTAMP DEFAULT NOW(),
                status TEXT,
                message TEXT
            );
        """)
        cur.execute(
            "INSERT INTO etl_log (status, message) VALUES (%s, %s);",
            (status, message)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Failed to log ETL status: {e}")
    finally:
        db_pool.putconn(conn)

# ----------------- ETL Process -----------------
def etl_process():
    try:
        log_etl("extracting")
        logger.info("Extracting data...")
        raw_data = extract_crypto_data()
        log_etl("extracted")

        log_etl("transforming")
        logger.info("Transforming data...")
        transformed_data = transform_data(raw_data)
        log_etl("transformed")

        log_etl("loading")
        logger.info("Loading data into DB...")
        insert_data(transformed_data, db_pool)
        log_etl("loaded")

        logger.info("ETL completed successfully.")
        log_etl("completed")
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        log_etl("error", str(e))

# ----------------- Scheduler -----------------
if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(etl_process, 'interval', minutes=5)
    scheduler.start()
    logger.info("ETL scheduler started. Press Ctrl+C to exit.")

    try:
        # Keep script running
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("ETL scheduler stopped.")