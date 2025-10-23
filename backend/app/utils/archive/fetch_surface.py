import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys
import time
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Handle imports based on how the script is run
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
else:
    from ..dictionary import TICKERS_DICT


def fetch_historical_options_data(spot, from_date, to_date, max_retries=5, retry_delay=10):
    """
    Fetch historical options data for a given ticker (spot) within a date range.
    
    Args:
        spot (str): Ticker symbol
        from_date (str): Start date in YYYY-MM-DD format
        to_date (str): End date in YYYY-MM-DD format
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        tuple: (options_data, spot) where options_data is the JSON response or None if failed
    """
    headers = {
        'Access-Token': 'q/N/OI3UnW+xmEUbYDK8FyIil8ymjM+J2VPefo+1qO2ni4kd2BIU4YGUzzTmAOJr--GcuwyydDFxVCE0+FC3yKoA==--NzM3YzdjZjkyYWQ0ZWJlNTZlZjkzOTVmOTIyMGNjODE='
    }

    url = f'https://api.oplab.com.br/v3/market/historical/options/{spot}/{from_date}/{to_date}'

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            options_data = response.json()
            logger.info(f"Historical Options Data for {spot} retrieved successfully.")
            return options_data, spot

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {spot}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to retrieve data for {spot} after {max_retries} attempts.")
                return None, spot

    return None, spot


def get_surface_data(ticker=None):
    """
    Retrieve volatility surface data for one ticker or multiple tickers.
    
    Args:
        ticker (str, optional): Specific ticker symbol. If None, uses TOP10 tickers.
        
    Returns:
        dict: Dictionary containing volatility surface data for requested tickers
    """
    all_tickers_data = {}
    tickers = [ticker] if ticker else TICKERS_DICT["TOP10"]
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    for ticker in tickers:
        historical_data, _ = fetch_historical_options_data(
            ticker, 
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        if not historical_data or not isinstance(historical_data, list):
            logger.warning(f"No data available for {ticker}")
            continue
            
        # Process historical data to get the latest time data
        ticker_data = []
        latest_time = datetime.min
        
        for date_data in historical_data:
            # Normalize data format
            if isinstance(date_data, dict):
                date_data = [date_data]
                
            if isinstance(date_data, list):
                for option in date_data:
                    option_time = datetime.strptime(option['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    
                    # If we found newer data, reset our collection
                    if option_time > latest_time:
                        latest_time = option_time
                        ticker_data = []  # Clear previous data
                        
                    # Add data from the latest timestamp
                    if option_time == latest_time:
                        ticker_data.append(option)
                        
        all_tickers_data[ticker] = ticker_data

    # Save data to JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    os.makedirs(export_dir, exist_ok=True)
    
    filename = 'volatility_surface.json'
    file_path = os.path.join(export_dir, filename)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_tickers_data, f, ensure_ascii=False, indent=4, default=str)

    logger.info(f"Volatility surface data saved to {file_path}")

    # Return requested data
    if ticker:
        return all_tickers_data.get(ticker, {"error": f"No data found for {ticker}"})
    return all_tickers_data


def get_surface_analysis(ticker=None):
    """
    Load and analyze previously saved volatility surface data.
    
    Args:
        ticker (str, optional): Specific ticker symbol to retrieve data for
        
    Returns:
        dict: Dictionary containing volatility surface data 
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    
    # Get the most recent file (assuming the file name has changed)
    files = [f for f in os.listdir(export_dir) if f.endswith('.json') and 
             (f == 'volatility_surface.json' or f.startswith('volatility_surface_'))]
    
    if not files:
        logger.warning("No volatility surface data files found.")
        return {}
    
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(export_dir, x)))
    json_file_path = os.path.join(export_dir, latest_file)
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            surface_data = json.load(json_file)
        
        if ticker:
            return {ticker: surface_data.get(ticker, {})}
        return surface_data
    
    except FileNotFoundError:
        logger.error(f"File not found at {json_file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file {json_file_path}")
        return {}


# This part is for testing purposes when running the script directly
if __name__ == "__main__":
    # Configure more verbose logging for direct script execution
    logger.setLevel(logging.DEBUG)
    
    # Test the get_surface_data function
    logger.info("Testing get_surface_data function")
    surface_data = get_surface_data()
    
    # Test the get_surface_analysis function
    logger.info("Testing get_surface_analysis function")
    analysis_data = get_surface_analysis()