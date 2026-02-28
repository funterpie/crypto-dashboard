# extract.py
import time
import requests
import json
from datetime import datetime

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 20,
    "page": 1,
    "sparkline": "false"
}

MAX_RETRIES = 5
RATE_LIMIT_DELAY = 5  # seconds to wait if rate limited


def extract_crypto_data():
    """
    Extract top 20 coins data from CoinGecko API.
    Handles rate limiting and retries.
    Returns: List of coin data (JSON)
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, params=PARAMS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Save raw JSON locally for logging
                filename = f"crypto_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)
                return data
            elif response.status_code == 429:
                print(f"Rate limited (attempt {attempt}). Waiting {RATE_LIMIT_DELAY}s...")
                time.sleep(RATE_LIMIT_DELAY)
            else:
                print(f"Unexpected status {response.status_code}. Retrying...")
                time.sleep(1)
        except requests.RequestException as e:
            print(f"Request failed (attempt {attempt}): {e}. Retrying...")
            time.sleep(2)
    raise Exception("Max retries exceeded. Extraction failed.")


if __name__ == "__main__":
    raw_data = extract_crypto_data()
    print(f"Extracted {len(raw_data)} coins successfully.")