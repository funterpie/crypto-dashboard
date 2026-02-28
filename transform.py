from datetime import datetime
import json

def transform_data(raw_data):
    """
    Transform raw crypto data:
    - Remove nulls
    - Convert numeric fields
    - Add volatility_score
    - Add extracted_at timestamp
    """
    transformed = []
    for coin in raw_data:
        if not all(k in coin and coin[k] is not None for k in ("current_price", "total_volume", "price_change_24h")):
            continue  # skip incomplete data
        
        transformed_coin = {
            "coin_id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "current_price": float(coin.get("current_price")),
            "market_cap": int(coin.get("market_cap") or 0),
            "total_volume": int(coin.get("total_volume") or 0),
            "price_change_24h": float(coin.get("price_change_24h") or 0.0),
            "market_cap_rank": int(coin.get("market_cap_rank") or 0),
            "volatility_score": abs(coin.get("price_change_24h") or 0.0) * (coin.get("total_volume") or 0),
            "extracted_at": datetime.now().isoformat()  # Adds timestamp in ISO format
        }
        transformed.append(transformed_coin)
    return transformed


if __name__ == "__main__":
    # Load the raw data from the JSON file
    with open('crypto_raw_20260301_010548 .json', 'r') as f:  # Adjust filename accordingly
        raw_data = json.load(f)
    
    # Transform the data
    transformed_data = transform_data(raw_data)
    
    # Optionally, save the transformed data to a new file for review or further use
    with open('crypto_transformed.json', 'w') as f:
        json.dump(transformed_data, f, indent=4)
    
    print(f"Transformed {len(transformed_data)} coins successfully.")