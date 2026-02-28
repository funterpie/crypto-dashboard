from apscheduler.schedulers.blocking import BlockingScheduler
from extract import extract_crypto_data
from transform import transform_data
from load import insert_data
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def etl_process():
    try:
        # Step 1: Extract Data
        logger.info("Starting data extraction...")
        raw_data = extract_crypto_data()

        # Step 2: Transform Data
        logger.info("Transforming data...")
        transformed_data = transform_data(raw_data)

        # Step 3: Load Data into DB
        logger.info("Loading data into the database...")
        insert_data(transformed_data)

        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.error(f"Error in ETL process: {e}")

if __name__ == "__main__":
    # Scheduler setup
    scheduler = BlockingScheduler()
    
    # Schedule the ETL process to run every 5 minutes
    scheduler.add_job(etl_process, 'interval', minutes=5)
    
    logger.info("ETL Scheduler started.")
    scheduler.start()