import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
    from utils.supabase_handler import SupabaseHandler
else:
    from ..dictionary import TICKERS_DICT
    from ..supabase_handler import SupabaseHandler

def fetch_historical_options_data(spot, from_date, to_date, max_retries=5, retry_delay=10):
    """Fetch historical options data from API with retry mechanism."""
    headers = {
        'Access-Token': 'q/N/OI3UnW+xmEUbYDK8FyIil8ymjM+J2VPefo+1qO2ni4kd2BIU4YGUzzTmAOJr--GcuwyydDFxVCE0+FC3yKoA==--NzM3YzdjZjkyYWQ0ZWJlNTZlZjkzOTVmOTIyMGNjODE='
    }

    url = f'https://api.oplab.com.br/v3/market/historical/options/{spot}/{from_date}/{to_date}'

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            options_data = response.json()
            logger.debug(f"Historical Options Data for {spot} retrieved successfully.")
            return options_data, spot
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed for {spot}: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to retrieve data for {spot} after {max_retries} attempts.")
                return None, spot
    
    return None, spot

def get_surface_data(ticker=None):
    """Process and save volatility surface data for specified tickers."""
    all_tickers_data = {}
    tickers = [ticker] if ticker else TICKERS_DICT["SURFACE"]
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2)
    date_format = "%Y-%m-%d"
    
    # Initialize Supabase handler
    try:
        supabase_handler = SupabaseHandler()
    except Exception as e:
        logger.error(f"Failed to initialize Supabase handler: {e}")
        supabase_handler = None
    
    for ticker in tickers:
        historical_data, _ = fetch_historical_options_data(ticker, 
                                                        start_date.strftime(date_format), 
                                                        end_date.strftime(date_format))
        
        if not historical_data or not isinstance(historical_data, list):
            logger.info(f"No data available for {ticker}")
            continue
            
        # Process historical data
        ticker_data = []
        latest_time = datetime.min
        for date_data in historical_data:
            if isinstance(date_data, dict):
                date_data = [date_data]
                
            if isinstance(date_data, list):
                for option in date_data:
                    option_time = datetime.strptime(option['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if option_time > latest_time:
                        latest_time = option_time
                        ticker_data = []  # Clear previous data
                    if option_time == latest_time:
                        ticker_data.append(option)
                        
        all_tickers_data[ticker] = ticker_data

    # Prepare data for CSV export and Supabase storage
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f'volatility_surface.csv'
    file_path = os.path.join(export_dir, filename)
    
    # Flatten data structure for CSV and Supabase
    all_options = []
    for ticker, options in all_tickers_data.items():
        for option in options:
            option_data = option.copy()
            option_data['underlying_ticker'] = ticker
            all_options.append(option_data)
    
    # Save to Supabase if data exists
    if all_options and supabase_handler:
        try:
            # Convert data to match the database schema
            db_records = []
            for option in all_options:
                # Convert time to datetime object
                time_str = option.get('time')
                time_obj = None
                if time_str:
                    try:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        # Try alternative format if needed
                        try:
                            time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            logger.warning(f"Could not parse time: {time_str}")
                
                # Convert due_date to datetime object
                due_date_str = option.get('due_date')
                due_date_obj = None
                if due_date_str:
                    try:
                        due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        # Try alternative format if needed
                        try:
                            due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            logger.warning(f"Could not parse due_date: {due_date_str}")
                
                # Prepare record for database
                db_record = {
                    'symbol': option.get('symbol'),
                    'time': time_obj.isoformat() if time_obj else None,
                    'spot': json.dumps(option.get('spot')) if isinstance(option.get('spot'), dict) else option.get('spot'),
                    'option_type': option.get('type'),
                    'due_date': due_date_obj.isoformat() if due_date_obj else None,
                    'strike': float(option.get('strike')) if option.get('strike') is not None else None,
                    'premium': float(option.get('premium')) if option.get('premium') is not None else None,
                    'maturity_type': option.get('maturity_type'),
                    'days_to_maturity': int(option.get('days_to_maturity')) if option.get('days_to_maturity') is not None else None,
                    'moneyness': option.get('moneyness'),
                    'delta': float(option.get('delta')) if option.get('delta') is not None else None,
                    'gamma': float(option.get('gamma')) if option.get('gamma') is not None else None,
                    'vega': float(option.get('vega')) if option.get('vega') is not None else None,
                    'theta': float(option.get('theta')) if option.get('theta') is not None else None,
                    'rho': float(option.get('rho')) if option.get('rho') is not None else None,
                    'volatility': float(option.get('volatility')) if option.get('volatility') is not None else None,
                    'poe': float(option.get('poe')) if option.get('poe') is not None else None,
                    'bs': float(option.get('bs')) if option.get('bs') is not None else None,
                    'underlying_ticker': option.get('underlying_ticker')
                }
                db_records.append(db_record)
            
            # Store in Supabase
            success = supabase_handler.store_options_surface_data(db_records)
            if success:
                logger.info(f"Surface data successfully stored in Supabase ({len(db_records)} records)")
            else:
                logger.warning("Failed to store surface data in Supabase")
        except Exception as e:
            logger.error(f"Error storing data in Supabase: {e}")
    
    # Save to CSV if data exists
    if all_options:
        df = pd.DataFrame(all_options)
        df.to_csv(file_path, index=False)
        logger.info(f"Volatility surface data saved to {file_path}")
    else:
        logger.warning("No data to save")

    # Return requested data
    if ticker:
        return all_tickers_data.get(ticker, {"error": f"No data found for {ticker}"})
    return all_tickers_data

def get_surface_analysis(ticker=None):
    """Retrieve the most recent volatility surface data from CSV file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    
    try:
        # Get the most recent CSV file
        files = [f for f in os.listdir(export_dir) 
                if f.startswith('volatility_surface_') and f.endswith('.csv')]
        
        if not files:
            logger.warning("No volatility surface data files found.")
            return {}
        
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(export_dir, x)))
        csv_file_path = os.path.join(export_dir, latest_file)
        
        # Read and process CSV data
        df = pd.read_csv(csv_file_path)
        surface_data = df.to_dict(orient='records')
        
        # Filter by ticker if specified
        if ticker:
            filtered_data = [option for option in surface_data if option['underlying_ticker'] == ticker]
            return {ticker: filtered_data} if filtered_data else {"error": f"No data found for {ticker}"}
        
        return surface_data
        
    except FileNotFoundError:
        logger.error(f"File not found in {export_dir}")
        return {}
    except pd.errors.EmptyDataError:
        logger.error(f"No data in CSV file")
        return {}
    except Exception as e:
        logger.error(f"Error processing surface data: {str(e)}")
        return {}

# This part is for testing purposes when running the script directly
if __name__ == "__main__":
    # Test the functions
    surface_data = get_surface_data()
    analysis_data = get_surface_analysis()