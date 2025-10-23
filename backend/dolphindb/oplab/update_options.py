# -*- coding: utf-8 -*-
import sys
import os
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from apps.utils.dict import TICKERS_DICT
import requests
import csv
from datetime import datetime, timedelta
import dolphindb as ddb
import pandas as pd
import time
import subprocess
import glob

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Create the new "zommalab" database and "vanilla" table in DolphinDB with range partitioning
create_db_and_table_script = """
def createZommalabAndVanillaTable() {
    if(!existsDatabase("dfs://zommalab")) {
        // Create the zommalab database with RANGE partitioning
        db = database("dfs://zommalab", RANGE, 2018.01.01..2030.12.31)
        print("zommalab database created successfully with RANGE partitioning")
    } else {
        db = database("dfs://zommalab")
        print("zommalab database already exists")
    }

    if(existsTable("dfs://zommalab", "vanilla")) {
        print("vanilla table already exists in zommalab database")
        return
    }

    schema = table(
        1:0, 
        ["symbol", "time", "spot_price", "spot_symbol", "option_type", "due_date", "strike", "premium",
         "maturity_type", "days_to_maturity", "moneyness", "delta", "gamma", "vega", "theta",
         "rho", "volatility", "poe", "bs"],
        [SYMBOL, TIMESTAMP, DOUBLE, SYMBOL, SYMBOL, DATE, DOUBLE, DOUBLE,
         SYMBOL, INT, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE,
         DOUBLE, DOUBLE, DOUBLE, DOUBLE]
    )
    
    // Create partitioned table with RANGE on time column
    db.createPartitionedTable(
        table=schema, 
        tableName="vanilla", 
        partitionColumns="time"
    )
    print("vanilla table created successfully in zommalab database with RANGE partitioning on time")
}
createZommalabAndVanillaTable()
"""

try:
    s.run(create_db_and_table_script)
    print("zommalab database and vanilla table setup completed with RANGE partitioning.")
except Exception as e:
    print(f"Error setting up zommalab database and vanilla table: {e}")
    sys.exit(1)


def fetch_save_and_load_options_data(spot, from_date, to_date, max_retries=5, retry_delay=10):
    headers = {
        'Access-Token': 'NV0MENA0YZ9bgJA/Wf+F+tROe+eYX9SpUBuhmxNNkeIVuQKf+/wtVkYT4gGo0uvg--tTAJG2No3ZgblMOUkEql4g==--NzllMzczOTg2ZWI5ZmJlN2U2MjBmMDA3NGIxODcxOWQ='
    }

    url = f'https://api.oplab.com.br/v3/market/historical/options/{spot}/{from_date}/{to_date}'

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            options_data = response.json()
            print(f"Options Data for {spot} retrieved successfully.")
            
            # Write CSV with column names matching the DolphinDB table schema
            csv_filename = f"{spot}_options.csv"
            with open(csv_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                header = ['symbol', 'time', 'spot_price', 'spot_symbol', 'option_type', 'due_date', 'strike', 'premium', 
                          'maturity_type', 'days_to_maturity', 'moneyness', 'delta', 'gamma', 'vega', 'theta', 
                          'rho', 'volatility', 'poe', 'bs']
                csvwriter.writerow(header)
                
                for option in options_data:
                    # Determine option type based on delta
                    option_type = 'CALL' if option['delta'] >= 0 else 'PUT'
                    
                    row = [
                        option['symbol'],
                        option['time'],
                        option['spot']['price'],
                        option['spot']['symbol'],
                        option_type,  # Use the determined option type
                        option['due_date'],
                        option['strike'],
                        option['premium'],
                        option['maturity_type'],
                        option['days_to_maturity'],
                        option['moneyness'],
                        option['delta'],
                        option['gamma'],
                        option['vega'],
                        option['theta'],
                        option['rho'],
                        option['volatility'],
                        option['poe'],
                        option['bs']
                    ]
                    csvwriter.writerow(row)
            
            print(f"Data has been written to {csv_filename}")
            return load_options_csv_to_dolphindb(spot)

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {spot}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to retrieve data for {spot} after {max_retries} attempts.")
                return 0, spot

    return 0, spot

def load_options_csv_to_dolphindb(spot):
    csv_filename = f"{spot}_options.csv"
    if not os.path.exists(csv_filename):
        print(f"File {csv_filename} not found. Skipping.")
        return 0, spot

    # Read the CSV file, explicitly specifying the 'option_type' column as string
    df = pd.read_csv(csv_filename, dtype={'option_type': str})
    print("Unique values in 'option_type':", df['option_type'].unique())

    # Convert date columns and remove timezone if necessary
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
    df['due_date'] = pd.to_datetime(df['due_date']).dt.tz_localize(None)

    # Convert numeric columns to float
    float_columns = ['spot_price', 'strike', 'premium', 'delta', 'gamma', 'vega', 'theta', 'rho', 'volatility', 'poe', 'bs']
    for col in float_columns:
        df[col] = df[col].astype('float64')
    df['days_to_maturity'] = df['days_to_maturity'].astype('int64')

    # Convert other columns to string (confirmation)
    string_columns = ['symbol', 'spot_symbol', 'maturity_type', 'moneyness']
    for col in string_columns:
        df[col] = df[col].astype(str)

    # Upload the DataFrame to DolphinDB
    s.upload({'data': df})

    # Script for insertion into DolphinDB
    script = """
    def insertOptionsData(data) {
        t = loadTable("dfs://zommalab", "vanilla")
        t.append!(select 
            symbol(symbol) as symbol, 
            time, 
            spot_price, 
            symbol(spot_symbol) as spot_symbol, 
            symbol(option_type) as option_type,
            due_date, 
            strike, 
            premium, 
            symbol(maturity_type) as maturity_type, 
            days_to_maturity, 
            symbol(moneyness) as moneyness, 
            delta, 
            gamma, 
            vega, 
            theta, 
            rho, 
            volatility, 
            poe, 
            bs 
            from data)
        return size(data)
    }
    insertOptionsData(data)
    """
    
    try:
        result = s.run(script)
        print(f"Options data for {spot} loaded successfully into DolphinDB! Inserted {result} rows.")
        return result, None
    except Exception as e:
        print(f"Error loading data for {spot} into DolphinDB: {e}")
        return 0, spot


def remove_duplicates():
    script = """
    def removeDuplicates() {
        vanillaTable = loadTable("dfs://zommalab", "vanilla")
        
        // Find duplicates based on symbol, time, and option_type
        duplicates = select symbol, time, option_type, count(*) as cnt from vanillaTable 
                     group by symbol, time, option_type having count(*) > 1
        
        if (size(duplicates) > 0) {
            // Select unique records
            uniqueData = select 
                symbol, time, first(spot_price) as spot_price, first(spot_symbol) as spot_symbol,
                option_type, first(due_date) as due_date, first(strike) as strike,
                first(premium) as premium, first(maturity_type) as maturity_type,
                first(days_to_maturity) as days_to_maturity, first(moneyness) as moneyness,
                first(delta) as delta, first(gamma) as gamma, first(vega) as vega,
                first(theta) as theta, first(rho) as rho, first(volatility) as volatility,
                first(poe) as poe, first(bs) as bs
            from vanillaTable
            group by symbol, time, option_type
            
            // Create a new partitioned table with unique data
            db = database("dfs://zommalab")
            db.dropTable("vanilla")  // Drop the old table
            newTable = db.createPartitionedTable(uniqueData, "vanilla", "time")
            newTable.append!(uniqueData)
        }
        
        return size(duplicates)
    }

    removeDuplicates()
    """
    
    # Run the script to remove duplicates
    num_duplicates_removed = s.run(script)
    if num_duplicates_removed == 0:
        print("No duplicates found in the vanilla table.")
    else:
        print(f"Removed {num_duplicates_removed} duplicate entries from the vanilla table.")

# Call this function after uploading data for all symbols


if __name__ == "__main__":
    # Set date range for data fetching
    today = datetime.now()
    from_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    total_inserted = 0
    failed_tickers = []

    for spot in TICKERS_DICT["TOP100"]:
        try:
            rows_inserted, failed_ticker = fetch_save_and_load_options_data(spot, from_date, to_date)
            total_inserted += rows_inserted
            if failed_ticker:
                failed_tickers.append(failed_ticker)
        except Exception as e:
            print(f"Error processing {spot}: {e}")
            failed_tickers.append(spot)

    print(f"Total rows inserted across all symbols: {total_inserted}")
    print(f"Tickers with unavailable information: {failed_tickers}")

    # Remove duplicates after processing all symbols
    remove_duplicates()

    try:
        total_rows = s.run("select count(*) from loadTable('dfs://zommalab', 'vanilla')")
        print(f"Total rows in the vanilla table after removing duplicates: {total_rows}")
    except Exception as e:
        print(f"Error getting total row count: {e}")

    # Save failed tickers to a file
    with open('failed_tickers.txt', 'w') as f:
        for ticker in failed_tickers:
            f.write(f"{ticker}\n")
    print("Failed tickers saved to failed_tickers.txt")

    # After successful operations, execute additional cleaning scripts
    print("Cleaning CSV data")


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
    print(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")