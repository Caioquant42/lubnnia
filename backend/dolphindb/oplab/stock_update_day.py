#!/usr/bin/env python3

import sys
import os
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)
from backend.apps.utils.dict import TICKERS_DICT

from datetime import datetime, timedelta
import requests
import csv
import dolphindb as ddb
import pandas as pd

import time
from datetime import datetime, timedelta
import subprocess

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Define a script to find and remove duplicates in the stockdata table
def remove_duplicates():
    script = """
    def removeDuplicates() {
        stockData = loadTable("dfs://oplab", "stockdata")
        
        // Find duplicates based on Time, Resolution, and Symbol
        duplicates = select Time, Resolution, Symbol, count(*) as cnt from stockData 
                     group by Time, Resolution, Symbol having count(*) > 1
        
        if (size(duplicates) > 0) {
            // Select unique records
            uniqueData = select Time, Resolution, Symbol, 
                                 first(Open) as Open, first(High) as High, first(Low) as Low,
                                 first(Close) as Close, first(Volume) as Volume, first(FVolume) as FVolume
                          from stockData
                          group by Time, Resolution, Symbol
            
            // Create a new partitioned table with unique data
            db = database("dfs://oplab")
            db.dropTable("stockdata")  // Drop the old table
            newTable = db.createPartitionedTable(uniqueData, "stockdata", "Time")
            newTable.append!(uniqueData)
        }
        
        return size(duplicates)
    }

    removeDuplicates()
    """
    
    # Run the script to remove duplicates
    num_duplicates_removed = s.run(script)

    # Print the result
    if num_duplicates_removed == 0:
        print("No duplicates found in the stockdata table.")
    else:
        print(f"Removed {num_duplicates_removed} duplicate entries from the stockdata table.")

def fetch_save_and_load_historical_data(symbol, resolution, from_date, to_date, max_retries=5, retry_delay=10):
    # Define API key and headers
    headers = {
        'Access-Token': 'NV0MENA0YZ9bgJA/Wf+F+tROe+eYX9SpUBuhmxNNkeIVuQKf+/wtVkYT4gGo0uvg--tTAJG2No3ZgblMOUkEql4g==--NzllMzczOTg2ZWI5ZmJlN2U2MjBmMDA3NGIxODcxOWQ='
    }

    # Define base URL with correct path parameters
    base_url = f'https://api.oplab.com.br/v3/market/historical/{symbol}/{resolution}'

    # Create parameters dictionary
    params = {
        'from': from_date,
        'to': to_date
    }

    for attempt in range(max_retries):
        try:
            # Make request with correctly formatted parameters
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # If we get here, the request was successful
            historical_data = response.json()
            print(f"Historical Data for {symbol} retrieved successfully.")
            
            # Write data to CSV file
            csv_filename = f"{symbol}_{resolution}.csv"
            with open(csv_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write header
                csvwriter.writerow(['Time','Resolution', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'FVolume'])
                
                # Write data rows
                for data_point in historical_data['data']:
                    csvwriter.writerow([
                        datetime.fromtimestamp(data_point['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),  # Convert milliseconds to date
                        resolution,  # Add resolution
                        symbol,  # Add symbol              
                        data_point['open'],
                        data_point['high'],
                        data_point['low'],
                        data_point['close'],
                        data_point['volume'],
                        data_point['fvolume']
                    ])
            
            print(f"Data has been written to {csv_filename}")
            
            # Now load the data into DolphinDB
            return load_csv_to_dolphindb(symbol, resolution)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            return 0  # Skip this symbol and continue with the next

    return 0  # If we get here, all attempts failed

def load_csv_to_dolphindb(symbol, resolution):
    try:
        csv_filename = f"{symbol}_{resolution}.csv"
        if not os.path.exists(csv_filename):
            print(f"File {csv_filename} not found. Skipping.")
            return 0

        # Read the CSV file
        df = pd.read_csv(csv_filename)

        # Convert the 'Time' column to datetime
        df['Time'] = pd.to_datetime(df['Time'])

        # Ensure all numeric columns are float64 (except Volume which should be int64)
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'FVolume']
        for col in numeric_columns:
            df[col] = df[col].astype('float64')
        df['Volume'] = df['Volume'].astype('int64')

        # Ensure 'Resolution' and 'Symbol' are string type and then convert 'Resolution' to SYMBOL type
        df['Resolution'] = df['Resolution'].astype(str).map(lambda x: s.run(f'`{x}'))  # Convert to SYMBOL type
        df['Symbol'] = df['Symbol'].astype(str)

        # Upload the data to the server
        s.upload({'data': df})

        # Insert data into the DolphinDB table
        script = """
        def insertData(data) {
            t = loadTable("dfs://oplab", "stockdata")
            t.append!(select date(Time) as Time, Resolution, Symbol, Open, High, Low, Close, long(Volume) as Volume, FVolume from data)
            return size(data)
        }
        insertData(data)
        """

        result = s.run(script)
        print(f"Data for {symbol} loaded successfully into DolphinDB! Inserted {result} rows.")
        return result

    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return 0  # Skip this symbol and continue with the next


# Main execution
if __name__ == "__main__":
    resolution = '1d'  # You can change this if needed
    
    today = datetime.now()
    from_date = (today - timedelta(days=20)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    total_inserted = 0

    # Iterate through each symbol in the TOP10 list
    for symbol in TICKERS_DICT["TODOS"]:
        rows_inserted = fetch_save_and_load_historical_data(symbol, resolution, from_date, to_date)
        total_inserted += rows_inserted

        print(f"Total rows inserted across all symbols: {total_inserted}")

        # Verify the total data
        try:
            total_rows = s.run("select count(*) from loadTable('dfs://oplab', 'stockdata')")
            print(f"Total rows in the table: {total_rows}")
        except Exception as e:
            print(f"Error fetching total rows: {e}")

    # Run the remove duplicates function
    remove_duplicates()

    print("Cleaning CSV data")
    import os
    import glob

    # Get the current directory
    current_directory = os.getcwd()

    # Find all .csv files in the current directory
    csv_files = glob.glob(os.path.join(current_directory, "*.csv"))

    # Delete each .csv file
    for file in csv_files:
        try:
            os.remove(file)
            #print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

    print("All .csv files deleted.")
