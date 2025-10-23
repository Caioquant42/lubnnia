# filepath: project/backend/app/utils/fetch_br_recommendations.py
import os
import sys
import json
import time
import csv
import io
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# Properly handle imports whether the script is run directly or as a module
if __name__ == "__main__":
    # Add the parent directory to sys.path so we can import from sibling modules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

    from utils.dictionary import TICKERS_DICT
    from utils.supabase_handler import SupabaseHandler
else:
    from .dictionary import TICKERS_DICT
    from .supabase_handler import SupabaseHandler

# Create a .env file in the backend directory if it doesn't exist
def ensure_env_file():
    # Find the backend directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(current_dir)
    backend_dir = os.path.dirname(app_dir)

    env_path = os.path.join(backend_dir, '.env')
    env_example_path = os.path.join(backend_dir, '.env.example')

    # If .env doesn't exist but .env.example does, copy it
    if not os.path.exists(env_path) and os.path.exists(env_example_path):
        try:
            import shutil
            shutil.copy(env_example_path, env_path)
            print(f"Created .env file from .env.example at {env_path}")
        except Exception as e:
            print(f"Error creating .env file: {e}")

# Ensure .env file exists
ensure_env_file()

# Initialize SupabaseHandler
supabase_handler = SupabaseHandler()

tickers = TICKERS_DICT.get('TODOS', [])



def get_recommendations_analysis(ticker=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")

    # Get the most recent file
    files = [f for f in os.listdir(export_dir) if f.startswith('all_B3_recommendations_') and f.endswith('.json')]
    if not files:
        print("No recommendations data files found.")
        return {}

    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(export_dir, x)))
    json_file_path = os.path.join(export_dir, latest_file)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            recommendations_data = json.load(json_file)

        # Return data for specific ticker if provided
        if ticker:
            return {ticker: recommendations_data.get(ticker, {})}

        return recommendations_data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {json_file_path}")
        return {}


class YData:
    def __init__(self, ticker_symbol, interval='1d', period='max', world=False, start_date=None, end_date=None):
        self.ticker_symbol = ticker_symbol
        self.interval = interval
        self.period = period
        self.world = world
        self.start_date = start_date
        self.end_date = end_date
        self.ticker = self._add_sa_to_tickers(self.ticker_symbol)
        self.stock_data = yf.Ticker(self.ticker)

    def _add_sa_to_tickers(self, tickers):
        return f"{tickers}.SA" if not self.world else tickers

    def get_fundamental_data_summary(self):
        try:
            info = self.stock_data.info

            # Define the specific fields we want to fetch
            desired_fields = [
                "currentPrice", "targetHighPrice", "targetLowPrice", "targetMeanPrice",
                "targetMedianPrice", "recommendationMean", "recommendationKey",
                "numberOfAnalystOpinions", "averageAnalystRating"
            ]
            # Create a dictionary with only the desired fields
            filtered_info = {field: info.get(field) for field in desired_fields if field in info}

            # Calculate additional metrics
            current_price = filtered_info.get('currentPrice')
            if (current_price is not None and current_price != 0):
                filtered_info['% Distance to Mean'] = ((filtered_info.get('targetMeanPrice', 0) - current_price) / current_price) * 100
                filtered_info['% Distance to Median'] = ((filtered_info.get('targetMedianPrice', 0) - current_price) / current_price) * 100
                filtered_info['% Distance to Low'] = ((filtered_info.get('targetLowPrice', 0) - current_price) / current_price) * 100
                filtered_info['% Distance to High'] = ((filtered_info.get('targetHighPrice', 0) - current_price) / current_price) * 100
            else:
                filtered_info['% Distance to Mean'] = None
                filtered_info['% Distance to Median'] = None
                filtered_info['% Distance to Low'] = None
                filtered_info['% Distance to High'] = None

            return filtered_info

        except Exception as e:
            print(f"Error retrieving fundamental data summary for {self.ticker}: {e}")
            return None

def save_all_fundamental_data_to_supabase():
    """Save all recommendation data to Supabase in CSV format"""
    # Create a list to hold all ticker data
    all_records = []
    
    timestamp = datetime.now().isoformat()
    
    for ticker in tickers:
        ydata = YData(ticker)
        ticker_data = ydata.get_fundamental_data_summary()
        if ticker_data:
            # Add ticker, exchange and timestamp to the data
            ticker_data['ticker'] = ticker
            ticker_data['exchange'] = 'BR'  # Exchange identifier for Brazil
            ticker_data['timestamp'] = timestamp
            all_records.append(ticker_data)
            print(f"{ticker} loaded successfully")
        else:
            print(f"No data found for {ticker}")
        time.sleep(1)
    
    if not all_records:
        print("No data collected for any tickers")
        return
    
    try:
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(all_records)
        
        # Fill any NaN values appropriately
        df = df.fillna({
            'recommendationKey': 'none',
            'numberOfAnalystOpinions': 0,
            'exchange': 'BR',
            '% Distance to Mean': -100.0,
            '% Distance to Median': -100.0,
            '% Distance to Low': -100.0,
            '% Distance to High': -100.0
        })
        
        # Save raw recommendations data to the recommendations table
        supabase_handler = SupabaseHandler()
        
        # 1. Store the data in CSV format
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        # Store the CSV data
        response = supabase_handler.store_recommendations_csv(csv_content)
        if response:
            print("All recommendations data saved to Supabase 'recommendations_records' table in CSV format.")
            print("Data processing and storage complete.")
        else:
            print("Failed to save recommendations to Supabase.")
            
            # Backup to local CSV file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            export_dir = os.path.join(current_dir, "export")
            os.makedirs(export_dir, exist_ok=True)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_file_path = os.path.join(export_dir, f"all_BR_recommendations_{timestamp_str}.csv")
            
            df.to_csv(csv_file_path, index=False)
            print(f"Recommendations data saved to local CSV file as backup: {csv_file_path}")

    except Exception as e:
        print(f"Error saving recommendations data to Supabase: {e}")
        # Backup to local CSV file
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            export_dir = os.path.join(current_dir, "export")
            os.makedirs(export_dir, exist_ok=True)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_file_path = os.path.join(export_dir, f"all_BR_recommendations.csv")
            
            if 'df' in locals():
                df.to_csv(csv_file_path, index=False)
                print(f"Recommendations data saved to local CSV file as backup: {csv_file_path}")
        except Exception as backup_error:
            print(f"Error saving backup file: {backup_error}")

def main():
    save_all_fundamental_data_to_supabase()
    print(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()