import subprocess
import sys
import os
from dolphindb import session
import pandas as pd
import json
from datetime import datetime
import numpy as np
import warnings

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
else:
    from .dictionary import TICKERS_DICT

# Suppress the specific deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning, message="DataFrameGroupBy.apply operated on the grouping columns.")

tickers = TICKERS_DICT.get('IBOV', [])
table_names = ['stockdata_15m', 'stockdata_60m', 'stockdata_1d', 'stockdata_1wk']

def calculate_rsi(data, window=14):
    delta = data['AdjClose'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def process_table(s, table_name):
    # Load the table from the distributed file system
    s.run(f't = loadTable("dfs://yfs", "{table_name}")')

    # Execute the query to filter the data by Time, Symbol, and select specific columns
    query = f'''
    select Datetime, Symbol, AdjClose 
    from t 
    where Datetime > 2024.01.01T03:00:00 and Symbol in {tickers}
    '''
    result = s.run(query)

    # Convert the query result to a DataFrame
    df = pd.DataFrame(result)
    df["Datetime"] = pd.to_datetime(df["Datetime"])

    # Remove rows with NaN values in AdjClose
    df = df.dropna(subset=['AdjClose'])

    # Function to calculate RSI for a single symbol
    def calculate_symbol_rsi(group):
        group = group.sort_values(by="Datetime")
        group["RSI"] = calculate_rsi(group)
        return group.iloc[-1]  # Return only the last row

    # Calculate RSI for each symbol
    latest_rsi = df.groupby("Symbol", group_keys=False).apply(calculate_symbol_rsi).reset_index(drop=True)

    # Filter for overbought (RSI > 70) and oversold (RSI < 30) conditions
    # Also ensure AdjClose is not NaN
    overbought = latest_rsi[(latest_rsi['RSI'] > 70) & (~np.isnan(latest_rsi['AdjClose']))].copy()
    oversold = latest_rsi[(latest_rsi['RSI'] < 30) & (~np.isnan(latest_rsi['AdjClose']))].copy()

    # Convert Datetime to string format
    overbought['Datetime'] = overbought['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    oversold['Datetime'] = oversold['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return {
        "overbought": overbought.to_dict('records'),
        "oversold": oversold.to_dict('records')
    }

def get_screener_analysis():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "export", "screener_overbought_oversold_rsi_results.json")
    
    print(f"Attempting to read file: {json_file_path}")  # Add this line
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            screener_data = json.load(json_file)
        print(f"Successfully read screener data: {screener_data}")  # Add this line
        return screener_data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {json_file_path}")
        return {}

def run_screener_analysis():
    # Connect to the DolphinDB server
    s = session()
    s.connect("46.202.149.154", 8848, "admin", "123456")

    # Process all tables and store results
    all_results = {}
    for table in table_names:
        print(f"Processing {table}...")
        all_results[table] = process_table(s, table)
        print(f"Completed processing {table}")

    # Custom JSON encoder to handle any remaining non-serializable objects
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            return super().default(obj)

    # Get the full path for the JSON file in the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_directory, 'export', 'screener_overbought_oversold_rsi_results.json')

    # Save all results to a single JSON file using the full path
    with open(json_file_path, 'w') as f:
        json.dump(all_results, f, indent=2, cls=CustomJSONEncoder)

    print("\nAll data processing completed.")
    print(f"Results have been saved to '{json_file_path}'")

    # Display summary for each table
    for table in table_names:
        print(f"\nSummary for {table}:")
        print(f"Overbought stocks: {len(all_results[table]['overbought'])}")
        print(f"Oversold stocks: {len(all_results[table]['oversold'])}")

    # Display a sample from each category for the first table
    first_table = table_names[0]
    print(f"\nSample of overbought stocks for {first_table}:")
    print(pd.DataFrame(all_results[first_table]['overbought']).head())
    print(f"\nSample of oversold stocks for {first_table}:")
    print(pd.DataFrame(all_results[first_table]['oversold']).head())

if __name__ == "__main__":
    # Function to run update_screener_data.py
    def run_update_screener_data():
        current_directory = os.path.dirname(os.path.abspath(__file__))
        update_script_path = os.path.join(current_directory, 'update_screener_data.py')
        
        print("Running update_screener_data.py...")
        try:
            subprocess.run([sys.executable, update_script_path], check=True)
            print("update_screener_data.py completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running update_screener_data.py: {e}")
            sys.exit(1)  # Exit if the update script fails

    # Run update_screener_data.py before the main code
    run_update_screener_data()

    # Run the main screener analysis
    run_screener_analysis()

    print(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")