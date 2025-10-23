# covered_call.py
import sys
import os
import json
import requests
import time
import cmath
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
log_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_directory, exist_ok=True)

# Create file handler
log_file = os.path.join(log_directory, 'covered_call.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Define the underlying assets
underlying = ["PETR4","VALE3", "BOVA11", "BBAS3", "BBDC4", "COGN3", "MGLU3", "ITUB4", "WEGE3", "EMBR3"]

call_bid = 'bid'  # change to bid/close if needed

# Define API key and headers
headers = {
    'Access-Token': os.getenv('OPLAB_ACCESS_TOKEN')
}

# Define base URL for the new API endpoint
option_base_url = 'https://api.oplab.com.br/v3/market/options'

# Define base URL for the new API endpoint
riskfree_base_url = 'https://api.oplab.com.br/v3/market/interest_rates/{id}'

# Define base URL for the new API endpoint
spot_base_url = 'https://api.oplab.com.br/v3/market/stocks'

def fetch_interest_rate(rate_id: str) -> Optional[Dict]:
    """
    Fetch interest rate data from the API.
    Args:
        rate_id (str): Interest rate ID ('CETIP' or 'SELIC')
    Returns:
        dict: Interest rate data or None if request fails
    """
    url = riskfree_base_url.format(id=rate_id)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"Successfully fetched {rate_id} rate data")
            return response.json()
        elif response.status_code == 204:
            logger.warning(f"No data available for {rate_id}")
        elif response.status_code == 401:
            logger.error("Unauthorized access")
        return None
    except Exception as e:
        logger.error(f"Error fetching {rate_id} data: {str(e)}")
        return None

def fetch_underlying_data(underlying_symbols, max_retries=3, delay=5):
    all_data = []
    
    for symbol in underlying_symbols:
        url = f"{spot_base_url}/{symbol}"
        logger.info(f"Fetching underlying data for {symbol}")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Filter the data to include only the desired fields
                filtered_data = {
                    "symbol": data.get("symbol"),
                    "type": data.get("type"),
                    "name": data.get("name"),
                    "open": data.get("open"),
                    "high": data.get("high"),
                    "low": data.get("low"),
                    "close": data.get("close"),
                    "volume": data.get("volume"),
                    "financial_volume": data.get("financial_volume"),
                    "trades": data.get("trades"),
                    "bid": data.get("bid"),
                    "ask": data.get("ask"),
                    "category": data.get("category"),
                    "contract_size": data.get("contract_size"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "parent_symbol": symbol  # Add parent_symbol to the filtered data
                }
                
                all_data.append(filtered_data)  # Append filtered data for each symbol
                logger.info(f"Successfully fetched data for {symbol}")
                break  # Exit retry loop if successful
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
    
    return all_data

def fetch_option_data(underlying_symbols, max_retries=3, delay=5):
    all_data = []
    
    for symbol in underlying_symbols:
        url = f"{option_base_url}/{symbol}"
        logger.info(f"Fetching option data for {symbol}")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                # Add parent_symbol to each option in the data
                for option in data:
                    option['parent_symbol'] = symbol
                all_data.extend(data)  # Combine data from all symbols
                logger.info(f"Successfully fetched option data for {symbol}")
                break  # Exit retry loop if successful
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
    
    return all_data

def save_raw_data_to_json(data, file_path):
    if not data:
        logger.warning("No data to save.")
        return
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        logger.info(f"Raw data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving raw data to {file_path}: {str(e)}")

def calculate_option_metrics(option, underlying_data, selic_rate):
    # Fetch the close price (spot_price) for the underlying asset
    parent_symbol = option.get('parent_symbol')
    spot_price = None

    # Find the underlying asset data for the parent_symbol
    for underlying_asset in underlying_data:
        if underlying_asset['symbol'] == parent_symbol:
            spot_price = underlying_asset.get('ask')
            break

    # If spot_price is not found, default to 0
    if spot_price is None:
        logger.warning(f"Could not find spot price for {parent_symbol}. Defaulting to 0.")
        spot_price = 0

    # Use the spot_price for calculations
    close_price = option.get(call_bid, 0)
    strike = option.get('strike', 0)
    days_to_maturity = option.get('days_to_maturity', 0)

    # Filter out options with zero or very low premiums (less than 0.01)
    if close_price < 0.01:
        logger.info(f"Filtering out option {option.get('symbol', 'unknown')} with low premium: {close_price}")
        return None

    # Determine moneyness
    if strike > spot_price:
        moneyness = 'OTM'
    else:
        moneyness = 'ITM'

    # Calculate intrinsic and extrinsic values
    intrinsic_value = max(spot_price - strike, 0)
    extrinsic_value = max(close_price - intrinsic_value, 0)
    protection = intrinsic_value / spot_price if spot_price != 0 else 0
    pm = spot_price - close_price
    embedded_interest = extrinsic_value / spot_price if spot_price != 0 else 0
    annual_return = (1 + embedded_interest)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0

    # Calculate CDI relative return
    cdi_relative_return = (annual_return * 100) / selic_rate if selic_rate != 0 else 0
    
    # If CDI relative return is less than 1, return None to filter out this option
    if cdi_relative_return <= 1:
        return None
    
    # Add new metrics
    spot_variation_to_max_return = (strike - spot_price) / spot_price if spot_price != 0 else 0
    pm_distance_to_profit = (strike - pm) / pm if pm != 0 else 0
    
    # Calculate combined score with weights
    # Normalize values to ensure score components are in a reasonable range
    
    # For annual_return - higher is better 
    norm_annual_return = max(0, annual_return) 
    
    # For spot_variation_to_max_return (lower is better)
    norm_spot_variation_to_max_return = 1 / (1 + abs(spot_variation_to_max_return)) if spot_variation_to_max_return != 0 else 0
    
    # For pm_distance_to_profit - higher is better 
    norm_pm_distance_to_profit = max(0, pm_distance_to_profit)
    
    # Assign weights based on importance
    weight_annual_return = 0.5  # 50% weight to annual return
    weight_spot_variation_to_max_return = 0.3    # 30% weight to free upside
    weight_pm_distance_to_profit = 0.2   # 20% weight to profit range
    
    # Calculate combined score
    score = (
        weight_annual_return * norm_annual_return +
        weight_spot_variation_to_max_return * norm_spot_variation_to_max_return +
        weight_pm_distance_to_profit * norm_pm_distance_to_profit
    )
    
    # If there's intrinsic value (ITM option), give a boost to the score
    if intrinsic_value > 0:
        protection_bonus = protection * 0.2  # Add up to 20% bonus for protection
        score += protection_bonus

    # Add calculated metrics to the option
    option['moneyness'] = moneyness
    option['intrinsic_value'] = intrinsic_value
    option['extrinsic_value'] = extrinsic_value
    option['pm'] = pm
    option['protection'] = protection
    option['embedded_interest'] = embedded_interest
    option['annual_return'] = annual_return
    option['spot_variation_to_max_return'] = spot_variation_to_max_return
    option['pm_distance_to_profit'] = pm_distance_to_profit
    option['score'] = score
    option['cdi_relative_return'] = cdi_relative_return  # Make sure this is included in the option data
    option['spot_price'] = spot_price  # Add spot_price to the option for reference

    return option

def save_processed_data_to_json(data, file_path):
    if not data:
        logger.warning("No data to save.")
        return
    
    # Save processed data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    logger.info(f"Processed data saved to {file_path}")

def filter_covered_calls(data):
    # Filter only CALL options with sufficient financial volume and non-zero premiums
    filtered_data = [
        option for option in data
        if (option['category'] == 'CALL' and 
            option.get('financial_volume', 0) > 1000 and
            option.get('bid', 0) >= 0.01)  # Filter out options with zero or very low premiums
    ]
    
    # Sort by annual return in descending order
    filtered_data.sort(key=lambda x: x.get('annual_return', 0), reverse=True)
    
    return filtered_data

def filter_option_fields(options):
    """Filter out unnecessary fields from options data."""
    fields_to_remove = [
        'contract_size',
        'exchange_id',
        'isin',
        'security_category',
        'quotationForm'
    ]
    
    filtered_options = []
    for option in options:
        filtered_option = {key: value for key, value in option.items() if key not in fields_to_remove}
        filtered_options.append(filtered_option)
    
    return filtered_options

def save_to_json(data, current_directory, selic_rate):
    if not data:
        logger.warning("No data to save.")
        return

    try:
        # Data already filtered for CDI relative return in calculate_option_metrics
        # Just need to sort and organize by maturity
        
        # Filter out unnecessary fields
        filtered_data = filter_option_fields(data)
        
        # Categorize data based on days_to_maturity
        less_than_14 = [option for option in filtered_data if option.get('days_to_maturity', 0) < 14]
        between_15_and_30 = [option for option in filtered_data if 15 <= option.get('days_to_maturity', 0) < 30]
        between_30_and_60 = [option for option in filtered_data if 30 <= option.get('days_to_maturity', 0) < 60]
        more_than_60 = [option for option in filtered_data if option.get('days_to_maturity', 0) >= 60]
        
        # Create a structured JSON with sections
        organized_data = {
            "less_than_14_days": less_than_14,
            "between_15_and_30_days": between_15_and_30,
            "between_30_and_60_days": between_30_and_60,
            "more_than_60_days": more_than_60
        }
        
        # Define file path for the single JSON output - using current_directory directly
        # instead of creating another export directory
        organized_json_path = os.path.join(current_directory, "covered_calls_organized.json")
        
        # Save organized JSON data to the file path
        with open(organized_json_path, 'w', encoding='utf-8') as f:
            json.dump(organized_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Organized data saved to {organized_json_path}")
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")

def get_covered_call_analysis() -> Dict[str, List[Dict[str, Any]]]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    
    covered_call_data = {}
    
    maturity_ranges = [
        "less_than_14_days",
        "between_15_and_30_days",
        "between_30_and_60_days",
        "more_than_60_days"
    ]
    
    for maturity_range in maturity_ranges:
        file_name = f"covered_calls_{maturity_range}.json"
        file_path = os.path.join(export_dir, file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                covered_call_data[maturity_range] = data
        except FileNotFoundError:
            logger.warning(f"File not found at {file_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file {file_path}")
    
    return covered_call_data

def main():
    logger.info("Starting covered call analysis")
    
    # Fetch SELIC rate once at the beginning
    logger.info("Fetching SELIC rate")
    selic_data = fetch_interest_rate('SELIC')
    if not selic_data or 'value' not in selic_data:
        logger.warning("Could not fetch SELIC rate. Using default value of 14.15")
        selic_rate = 14.15
    else:
        selic_rate = selic_data['value']
        logger.info(f"SELIC rate: {selic_rate}")
    
    # Fetch underlying data
    logger.info("Fetching underlying data")
    underlying_data = fetch_underlying_data(underlying)
    
    # Fetch raw option data
    logger.info("Fetching option data")
    raw_data = fetch_option_data(underlying)
    
    # Calculate option metrics
    logger.info("Calculating option metrics")
    processed_data = []
    for option in raw_data:
        processed_option = calculate_option_metrics(option, underlying_data, selic_rate)
        if processed_option:  # Only add options that pass the CDI relative return threshold
            processed_data.append(processed_option)
    
    # Filter for covered calls
    logger.info("Filtering covered calls")
    covered_calls = filter_covered_calls(processed_data)
    
    # Save processed data
    current_directory = os.path.dirname(os.path.abspath(__file__))
    export_directory = os.path.join(current_directory, "export")
    
    # Create export directory if it doesn't exist
    os.makedirs(export_directory, exist_ok=True)
    
    logger.info("Saving filtered data")
    save_to_json(covered_calls, export_directory, selic_rate)
    logger.info("Covered call analysis completed")

if __name__ == "__main__":
    main()