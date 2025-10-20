# fetch_options_data.py
# Fetches Options Quoted Data

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("oplab_options")

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
    from utils.supabase_handler import SupabaseHandler
else:
    from ..dictionary import TICKERS_DICT
    from ..supabase_handler import SupabaseHandler

# Define API key and headers
headers = {
    'Access-Token': 'q/N/OI3UnW+xmEUbYDK8FyIil8ymjM+J2VPefo+1qO2ni4kd2BIU4YGUzzTmAOJr--GcuwyydDFxVCE0+FC3yKoA==--NzM3YzdjZjkyYWQ0ZWJlNTZlZjkzOTVmOTIyMGNjODE='
}

def fetch_options(symbol, max_retries=3, delay=2):
    """
    Fetch options data for a specific symbol from OpLab API
    
    Args:
        symbol (str): The symbol to fetch options data for
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        delay (int, optional): Delay between retries in seconds. Defaults to 2.
        
    Returns:
        pd.DataFrame: DataFrame containing options data, or None if failed
    """
    url = f'https://api.oplab.com.br/v3/market/options/{symbol}'
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            options_data = response.json()
            
            if not options_data:
                logger.debug(f"No data received for {symbol}")
                return None
            
            df = pd.DataFrame(options_data)
            logger.debug(f"Received {len(df)} options records for {symbol}")
            
            # Add fetch timestamp to track when data was retrieved
            df['fetch_timestamp'] = datetime.now().isoformat()
            
            # Convert all data to strings immediately
            for column in df.columns:
                df[column] = df[column].astype(str)
                # Replace 'nan' and 'None' strings with empty strings
                df[column] = df[column].replace({'nan': '', 'None': '', 'NaT': ''})
            
            return df
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
            if attempt < max_retries - 1:
                logger.debug(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to retrieve data for {symbol} after {max_retries} attempts")
                return None
        except Exception as e:
            logger.error(f"Unexpected error for {symbol}: {e}")
            return None

def save_options_to_supabase(combined_df):
    """
    Save options data to Supabase database
    
    Args:
        combined_df (pd.DataFrame): DataFrame containing options data
        
    Returns:
        bool: True if successful, False otherwise
    """
    if combined_df is None or combined_df.empty:
        logger.warning("No options data to save to Supabase")
        return False
    
    try:
        # Convert DataFrame to records for Supabase
        records = combined_df.to_dict(orient='records')
        
        # Initialize Supabase handler and store data
        handler = SupabaseHandler()
        
        # Changed to use oplab_realtime_options_records table instead of oplab_options_data
        result = handler.store_oplab_realtime_options_records(records)
        
        if result:
            logger.info(f"Successfully saved {len(records)} options records to Supabase database")
        else:
            logger.error("Failed to save options data to Supabase database")
        
        return result
    except Exception as e:
        logger.error(f"Error storing OpLab options data in Supabase: {e}")
        return False

def get_options_data(ticker=None):
    """
    Fetch options data for one or more tickers
    
    Args:
        ticker (str, optional): Specific ticker to fetch data for. 
                               If None, fetches data for all tickers in TOP10.
    
    Returns:
        dict: Dictionary with ticker as key and DataFrame as value
    """
    all_tickers_data = {}
    all_dataframes = {}

    tickers = [ticker] if ticker else TICKERS_DICT["TOP10"]
    logger.info(f"Fetching options data for {len(tickers)} tickers")

    for ticker in tickers:
        logger.info(f"Processing {ticker}...")
        ticker_df = fetch_options(ticker)
        if ticker_df is not None:
            ticker_df['ticker'] = ticker  # Add ticker column to identify the source
            all_dataframes[ticker] = ticker_df
            all_tickers_data[ticker] = ticker_df  # Store DataFrame directly
        time.sleep(1)  # Small delay to avoid potential rate limiting

    # Save the data to a single CSV file in the export directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    os.makedirs(export_dir, exist_ok=True)
    
    # If we have data for multiple tickers, combine them into one DataFrame and save
    if all_dataframes:
        # Combine all DataFrames into one
        combined_df = pd.concat(all_dataframes.values(), ignore_index=True)
        
        # First save to Supabase database
        logger.info("Saving options data to Supabase database...")
        try:
            save_options_to_supabase(combined_df)
        except Exception as e:
            logger.error(f"Error storing OpLab options data in Supabase: {e}")
        
        # Save to local CSV file
        combined_filename = 'realtime_options_data.csv'
        combined_file_path = os.path.join(export_dir, combined_filename)
        combined_df.to_csv(combined_file_path, index=False)
        logger.info(f"Real time Options data saved to {combined_file_path}")
    else:
        logger.warning("No data available to save")

    if ticker:
        return all_tickers_data.get(ticker)
    return all_tickers_data

def get_options_analysis():
    """
    Get options data for analysis from either Supabase or local CSV file
    
    Returns:
        dict: Dictionary of DataFrames grouped by ticker
    """
    try:
        # First try to get data from Supabase
        handler = SupabaseHandler()
        data = handler.get_latest_options_data()
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            logger.debug(f"Retrieved {len(data)} options records from Supabase")
            # Group the data by ticker
            tickers_data = {}
            for ticker, group_df in data.groupby('ticker'):
                tickers_data[ticker] = group_df
            return tickers_data
    except Exception as e:
        logger.warning(f"Error retrieving data from Supabase: {e}")
        logger.debug("Falling back to local CSV file...")
    
    # Fall back to local CSV file if Supabase retrieval fails
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    csv_file_path = os.path.join(export_dir, 'realtime_options_data.csv')
    
    try:
        if not os.path.exists(csv_file_path):
            logger.error(f"Error: File not found at {csv_file_path}")
            return {}
            
        df = pd.read_csv(csv_file_path)
        # Group the data by ticker
        tickers_data = {}
        for ticker, group_df in df.groupby('ticker'):
            tickers_data[ticker] = group_df
        return tickers_data
    except FileNotFoundError:
        logger.error(f"Error: File not found at {csv_file_path}")
        return {}
    except pd.errors.EmptyDataError:
        logger.error(f"Error: Empty CSV file at {csv_file_path}")
        return {}
    except Exception as e:
        logger.exception(f"Error reading CSV file {csv_file_path}: {e}")
        return {}

def get_surface_analysis(ticker=None):
    """
    Get surface analysis data for one or all tickers
    
    Args:
        ticker (str, optional): Specific ticker to get data for. If None, gets data for all tickers.
        
    Returns:
        dict: Dictionary with ticker as key and DataFrame as value
    """
    options_data = get_options_analysis()
    if ticker:
        return {ticker: options_data.get(ticker, {})}
    return options_data

def test_api_accessibility(test_symbol="PETR4", timeout=10):
    """
    Test if the OpLab API is accessible before running the main code.
    
    Args:
        test_symbol (str): Symbol to use for the API test (default: "PETR4")
        timeout (int): Request timeout in seconds
        
    Returns:
        bool: True if API is accessible, False otherwise
    """
    logger.info(f"Testing OpLab API accessibility with symbol {test_symbol}...")
    url = f'https://api.oplab.com.br/v3/market/options/{test_symbol}'
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes
        logger.info("API test successful. OpLab API is accessible.")
        return True
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        logger.error(f"API test failed: {str(e)}")
        logger.error("OpLab API is not accessible. Please check your internet connection or API credentials.")
        return False

# This part is for testing purposes when running the script directly
if __name__ == "__main__":
    if test_api_accessibility():
        logger.info("Starting options data fetch process...")
        all_data = get_options_data()
        
        # Fixed the ambiguous truth value error by explicitly checking if the dictionary is empty
        if all_data and len(all_data) > 0:
            logger.info(f"Successfully fetched data for {len(all_data)} tickers")
            
            # Test the get_options_analysis function
            logger.debug("Testing options analysis functionality...")
            analysis_data = get_options_analysis()
            
            # Check if analysis_data dictionary is not empty
            if analysis_data and len(analysis_data) > 0:
                logger.info(f"Analysis data retrieved for {len(analysis_data)} tickers")
            else:
                logger.warning("No analysis data could be retrieved")
        else:
            logger.warning("No data could be fetched from the API")
        
        logger.info(f"Process completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        logger.error("Script execution aborted because the API is not accessible.")