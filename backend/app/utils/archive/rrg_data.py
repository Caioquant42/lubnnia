# app/utils/rrg_data.py

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import dolphindb as ddb
from datetime import datetime, timedelta
import json
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rrg_data.log'))
    ]
)
logger = logging.getLogger('rrg_data')

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
else:
    from ..dictionary import TICKERS_DICT

# Create a session and connect to the DolphinDB server
s = ddb.session()
try:
    s.connect("46.202.149.154", 8848, "admin", "123456")
    logger.info("Connected to DolphinDB server")
except Exception as e:
    logger.error(f"Failed to connect to DolphinDB server: {e}")

# Define API key and headers for the external API
headers = {
    'Access-Token': 'q/N/OI3UnW+xmEUbYDK8FyIil8ymjM+J2VPefo+1qO2ni4kd2BIU4YGUzzTmAOJr--GcuwyydDFxVCE0+FC3yKoA==--NzM3YzdjZjkyYWQ0ZWJlNTZlZjkzOTVmOTIyMGNjODE='
}

# Define base URL for the API endpoint
base_url = 'https://api.oplab.com.br/v3/market/historical'

def fetch_stockdata_1d(tickers, start_date=None, end_date=None):
    """
    Fetch stock data from DolphinDB for the given tickers and date range
    """
    start_time = datetime.now()
    
    # If no dates are provided, use the last 60 days
    if not start_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    # Convert dates to string format if they're datetime objects
    if isinstance(start_date, datetime):
        start_date = start_date.strftime('%Y.%m.%dT%H:%M:%S')
    if isinstance(end_date, datetime):
        end_date = end_date.strftime('%Y.%m.%dT%H:%M:%S')

    # Convert tickers list to a string format for the query
    tickers_str = '(' + ', '.join([f'"{ticker}"' for ticker in tickers]) + ')'

    # DolphinDB script to fetch data from stockdata_1d
    script = f"""
    t = loadTable("dfs://yfs", "stockdata_1d")
    select Datetime, Symbol, AdjClose 
    from t 
    where Datetime between {start_date} : {end_date} and Symbol in {tickers_str}
    """

    try:
        # Execute the script and fetch the data
        data = s.run(script)
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Fetched {len(df)} rows from stockdata_1d in {elapsed:.2f} seconds")
        return df
    except Exception as e:
        logger.error(f"Error fetching data from DolphinDB: {e}")
        return None

def fetch_historical_data(symbol, resolution, start_date, end_date, amount=None, raw=False, smooth=False, df='iso'):
    """
    Fetch historical data from external API
    """
    params = {
        'from': start_date,
        'to': end_date,
        'amount': amount,
        'raw': str(raw).lower(),
        'smooth': str(smooth).lower(),
        'df': df
    }
    
    url = f"{base_url}/{symbol}/{resolution}"
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Successfully fetched data for {symbol}")
            return response.json()
        else:
            logger.warning(f"Failed to retrieve data for {symbol}. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {symbol}: {str(e)}")
        return None

def fetch_historical_data_parallel(symbols, resolution, start_date, end_date, max_workers=10):
    """
    Fetch historical data for multiple symbols in parallel
    """
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a dictionary of futures
        future_to_symbol = {
            executor.submit(
                fetch_historical_data, symbol, resolution, start_date, end_date
            ): symbol for symbol in symbols
        }
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                data = future.result()
                if data and 'data' in data:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
    
    return results

def calculate_rs_ratio(security, benchmark):
    """
    Calculate the RS-Ratio between a security and a benchmark
    """
    rs = security / benchmark
    rs_ratio = rs / rs.rolling(window=14).mean() * 100  # Smoothed RS
    return rs_ratio

def calculate_rs_momentum(rs_ratio):
    """
    Calculate the RS-Momentum from an RS-Ratio series
    """
    rs_momentum = (rs_ratio.pct_change(periods=1) + 1) * 100  # Shift to center around 1
    return rs_momentum

def get_rrg_data():
    """
    Load the RRG data from the JSON file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "export", "rrg_data.json")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            rrg_data = json.load(json_file)
        logger.info(f"RRG data loaded with {len(rrg_data)} tickers")
        
        # Standardize the field names
        for ticker in rrg_data:
            if 'RS-Ratio' in rrg_data[ticker]:
                rrg_data[ticker]['RS_Ratio'] = rrg_data[ticker].pop('RS-Ratio')
            if 'RS-Momentum' in rrg_data[ticker]:
                rrg_data[ticker]['RS_Momentum'] = rrg_data[ticker].pop('RS-Momentum')
        
        return rrg_data
    except FileNotFoundError:
        logger.error(f"Error: File not found at {json_file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error: Invalid JSON in file {json_file_path}")
        return {}

def calculate_rrg(data, benchmark):
    """
    Calculate RRG data for all tickers compared to a benchmark
    """
    start_time = datetime.now()
    logger.info(f"Calculating RRG data for {len(data.columns)} tickers against {benchmark}")
    
    rs_ratios = {}
    rs_momentums = {}
    json_data = {}

    # First, calculate all ratios and momentums to avoid redundant calculations
    for ticker in data.columns:
        if ticker != benchmark and not data[ticker].isna().all() and not data[benchmark].isna().all():
            try:
                rs_ratios[ticker] = calculate_rs_ratio(data[ticker], data[benchmark])
                rs_momentums[ticker] = calculate_rs_momentum(rs_ratios[ticker])
            except Exception as e:
                logger.warning(f"Error calculating RRG for {ticker}: {str(e)}")
    
    # Then prepare the JSON output
    for ticker in rs_ratios:
        last_rs_ratio = rs_ratios[ticker].dropna().tail(5)
        last_rs_momentum = rs_momentums[ticker].dropna().tail(5)
        last_dates = pd.to_datetime(last_rs_ratio.index).strftime('%Y-%m-%d').tolist()

        if len(last_dates) > 0:
            json_data[ticker] = {
                "Dates": last_dates,
                "RS_Ratio": [round(x, 8) for x in last_rs_ratio.tolist()],
                "RS_Momentum": [round(x, 8) for x in last_rs_momentum.tolist()]
            }
        else:
            logger.warning(f"{ticker} - No valid data for RRG calculation")

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"RRG calculation completed in {elapsed:.2f} seconds for {len(json_data)} tickers")
    return json_data

def save_json_data(json_data, filename):
    """
    Save RRG data to a JSON file with consistent formatting
    """
    # Ensure all data structures have the same fields and formats
    standardized_data = {}
    for ticker, data in json_data.items():
        standardized_data[ticker] = {
            "Dates": data.get("Dates", []),
            "RS_Ratio": data.get("RS_Ratio", []),
            "RS_Momentum": data.get("RS_Momentum", [])
        }
    
    # Ensure the export directory exists
    current_directory = os.path.dirname(os.path.abspath(__file__))
    export_directory = os.path.join(current_directory, "export")
    os.makedirs(export_directory, exist_ok=True)
    
    # Save the data to a JSON file in the export directory
    json_filename = os.path.join(export_directory, filename)
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(standardized_data, json_file, indent=4, ensure_ascii=False)
    
    logger.info(f"RRG data saved to {json_filename}")

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info("Starting RRG data calculation")
    
    # Define the date range (60 days from today)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    # 1. Fetch data from API for index tickers
    api_tickers = [
        "IBOV", "IBXX", "IBXL", "IBRA", "IGCX", "ITAG", "IGNM", "IGCT",
        "IDIV", "MLCX", "SMLL", "IVBX2", "ICO2", "ISEE", "ICON", "IEEX",
        "IFNC", "IMOB", "INDX", "IMAT", "UTIL", "IFIX", "BDRX"
    ]
    
    # Fetch API data in parallel
    logger.info(f"Fetching data for {len(api_tickers)} API tickers in parallel")
    api_results = fetch_historical_data_parallel(
        api_tickers, 
        '1d', 
        start_date.strftime('%Y-%m-%d'), 
        end_date.strftime('%Y-%m-%d')
    )
    
    # Process API results
    df_list_api = []
    for ticker, result in api_results.items():
        if result and 'data' in result:
            for entry in result['data']:
                df_list_api.append({
                    'Datetime': pd.to_datetime(entry['time']),
                    'Symbol': ticker,
                    'AdjClose': entry['close']
                })
    
    df_api = pd.DataFrame(df_list_api)
    
    if not df_api.empty:
        data_api = df_api.pivot(index='Datetime', columns='Symbol', values='AdjClose')
        
        # Calculate RRG for API data
        json_data_api = calculate_rrg(data_api, 'IBOV')
    else:
        logger.warning("No API data available")
        json_data_api = {}

    # 2. Fetch data from DolphinDB for all tickers
    ibov_tickers = TICKERS_DICT.get("TODOS", []) + ['BOVA11']  # Add BOVA11 to the list of tickers
    logger.info(f"Fetching data for {len(ibov_tickers)} DolphinDB tickers")
    
    df_dolphin = fetch_stockdata_1d(ibov_tickers, start_date, end_date)
    
    if df_dolphin is not None and not df_dolphin.empty:
        # Convert Datetime to pandas datetime
        df_dolphin['Datetime'] = pd.to_datetime(df_dolphin['Datetime'])
        
        data_dolphin = df_dolphin.pivot(index='Datetime', columns='Symbol', values='AdjClose')
        
        # Calculate RRG for DolphinDB data using BOVA11 as benchmark
        json_data_dolphin = calculate_rrg(data_dolphin, 'BOVA11')
    else:
        logger.error("Error: Unable to fetch data from DolphinDB or data is empty")
        json_data_dolphin = {}

    # Combine results
    json_data = {**json_data_api, **json_data_dolphin}
    
    # Save the combined data
    save_json_data(json_data, 'rrg_data.json')
    
    total_elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"RRG data calculation completed in {total_elapsed:.2f} seconds")
    logger.info(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")