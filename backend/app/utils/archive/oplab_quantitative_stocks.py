import sys
import os
import json
import requests
import csv
import datetime
from datetime import datetime
import time

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

# Define base URL for "Consultar uma ação" endpoint
base_url = 'https://api.oplab.com.br/v3/market/stocks/{symbol}'

filtered_stocks = []

def convert_timestamp(ms_timestamp):
    if ms_timestamp is None:
        return None
    timestamp = ms_timestamp / 1000  # convert milliseconds to seconds
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def fetch_stock_data(symbol, max_retries=3, delay=5):
    url = base_url.format(symbol=symbol)
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)  # Add a timeout
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            print(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
                return None

def process_stock_data(stock):
    if not stock:
        return None

    filtered_stock = {
        'symbol': stock.get('symbol'),
        'type': stock.get('type'),
        'name': stock.get('name'),
        'open': stock.get('open'),
        'high': stock.get('high'),
        'low': stock.get('low'),
        'close': stock.get('close'),
        'volume': stock.get('volume'),
        'financial_volume': stock.get('financial_volume'),
        'trades': stock.get('trades'),
        'bid': stock.get('bid'),
        'ask': stock.get('ask'),
        'category': stock.get('category'),
        'contract_size': stock.get('contract_size'),
        'created_at': stock.get('created_at'),
        'updated_at': stock.get('updated_at'),
        'variation': stock.get('variation'),
        'ewma_1y_max': stock.get('ewma_1y_max'),
        'ewma_1y_min': stock.get('ewma_1y_min'),
        'ewma_1y_percentile': stock.get('ewma_1y_percentile'),
        'ewma_1y_rank': stock.get('ewma_1y_rank'),
        'ewma_6m_max': stock.get('ewma_6m_max'),
        'ewma_6m_min': stock.get('ewma_6m_min'),
        'ewma_6m_percentile': stock.get('ewma_6m_percentile'),
        'ewma_6m_rank': stock.get('ewma_6m_rank'),
        'ewma_current': stock.get('ewma_current'),
        'has_options': stock.get('has_options'),
        'iv_1y_max': stock.get('iv_1y_max'),
        'iv_1y_min': stock.get('iv_1y_min'),
        'iv_1y_percentile': stock.get('iv_1y_percentile'),
        'iv_1y_rank': stock.get('iv_1y_rank'),
        'iv_6m_max': stock.get('iv_6m_max'),
        'iv_6m_min': stock.get('iv_6m_min'),
        'iv_6m_percentile': stock.get('iv_6m_percentile'),
        'iv_6m_rank': stock.get('iv_6m_rank'),
        'iv_current': stock.get('iv_current'),
        'middle_term_trend': stock.get('middle_term_trend'),
        'semi_return_1y': stock.get('semi_return_1y'),
        'short_term_trend': stock.get('short_term_trend'),
        'stdv_1y': stock.get('stdv_1y'),
        'stdv_5d': stock.get('stdv_5d'),
        'beta_ibov': stock.get('beta_ibov'),
        'garch11_1y': stock.get('garch11_1y'),
        'isin': stock.get('isin'),
        'correl_ibov': stock.get('correl_ibov'),
        'entropy': stock.get('entropy'),
        'sector': stock.get('sector'),
        'cvmCode': stock.get('cvmCode'),
        'currency': stock.get('currency'),
        'currencyScale': stock.get('currencyScale'),
        'marketMaker': stock.get('marketMaker'),
        'previousClose': stock.get('previousClose'),
        'time': convert_timestamp(stock.get('time'))
    }
    return filtered_stock

def get_ibov_stocks():
    filtered_stocks = []
    for symbol in TICKERS_DICT["IBOV"]:  # Fixed from "IBEE" to "IBOV"
        print(f"Fetching {symbol} stock data")
        stock_data = fetch_stock_data(symbol)
        if stock_data:
            filtered_stock = process_stock_data(stock_data)
            if filtered_stock:
                filtered_stocks.append(filtered_stock)
        time.sleep(1)  # Small delay to avoid potential rate limiting
    return filtered_stocks

# Removing the JSON methods, keeping only CSV
def getstatic_ibov_stocks():
    """
    Legacy function that now calls getstatic_ibov_stocks_csv for backward compatibility
    """
    return getstatic_ibov_stocks_csv()

def save_stocks_to_csv(stocks, filename):
    if not stocks:
        print("No data to save to CSV")
        return
        
    # Get the keys from the first stock to use as headers
    fieldnames = stocks[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for stock in stocks:
            writer.writerow(stock)

def save_stocks_to_supabase(stocks):
    """
    Save the stocks data directly to Supabase
    """
    if not stocks:
        print("No data to save to Supabase")
        return False
    
    try:
        handler = SupabaseHandler()
        success = handler.store_oplab_stocks_data(stocks)
        
        if success:
            print(f"Successfully saved {len(stocks)} OpLab stock records to Supabase")
        else:
            print("Failed to save data to Supabase")
        
        return success
    except Exception as e:
        print(f"Error saving data to Supabase: {str(e)}")
        return False
            
def getstatic_ibov_stocks_csv():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_directory, "export", "IBOV_stocks.csv")
    
    stocks = []
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            stocks = list(reader)
        return stocks
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
        return []
    except Exception as e:
        print(f"Error: Unable to read CSV file {csv_file_path}: {str(e)}")
        return []

def test_api_accessibility(test_symbol="PETR4", timeout=10):
    """
    Test if the OpLab API is accessible before running the main code.
    
    Args:
        test_symbol: Symbol to use for the API test (default: "PETR4")
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if API is accessible, False otherwise
    """
    print(f"Testing OpLab API accessibility with symbol {test_symbol}...")
    url = base_url.format(symbol=test_symbol)
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("API test successful. OpLab API is accessible.")
        return True
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        print(f"API test failed: {str(e)}")
        print("OpLab API is not accessible. Please check your internet connection or API credentials.")
        return False

if __name__ == '__main__':
    if test_api_accessibility():
        stocks = get_ibov_stocks()
        
        current_directory = os.path.dirname(os.path.abspath(__file__))
        export_directory = os.path.join(current_directory, "export")
        os.makedirs(export_directory, exist_ok=True)

        # Save to CSV file
        csv_filename = os.path.join(export_directory, "IBOV_stocks.csv")
        save_stocks_to_csv(stocks, csv_filename)
        print(f"Data has been written to {csv_filename}")
        
        # Also save to Supabase
        print("Saving data to Supabase...")
        supabase_success = save_stocks_to_supabase(stocks)
        if supabase_success:
            print("Data has been successfully stored in Supabase database")
        else:
            print("Failed to store data in Supabase database")

        print(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Script execution aborted because the API is not accessible.")
        print("Please check your internet connection or API credentials and try again.")