#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(project_root)
sys.path.insert(0, project_root)
from dictionary import TICKERS_DICT
import yfinance as yf
import pandas as pd
from datetime import timezone
import dolphindb as ddb
import time

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

def add_sa_to_tickers(tickers):
    return [ticker + '.SA' for ticker in tickers]

def fetch_and_save_data(ticker_symbol, interval):
    """
    Fetch historical stock data for a given ticker symbol and interval.
    Saves the data to a CSV file and returns the DataFrame.
    """
    try:
        stock_data = yf.Ticker(ticker_symbol)
        # Fetch historical data with the specified interval
        historical_data = stock_data.history(period="1mo", interval=interval, auto_adjust=False)
        print(f"Fetching data for {ticker_symbol} at interval {interval}")
        #print(historical_data)

        # Reset index to make datetime a column
        historical_data = historical_data.reset_index()
        
        # Convert datetime to UTC and then to nanoseconds since epoch
        historical_data['Datetime'] = pd.to_datetime(historical_data['Datetime'], utc=True)
        historical_data['Datetime'] = historical_data['Datetime'].astype('int64') // 10**6
        
        # Add Symbol column right after Datetime
        historical_data.insert(1, 'Symbol', ticker_symbol.replace('.SA', ''))

        # Mapeamento e conversÃ£o de tipos
        historical_data = historical_data.rename(columns={
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Adj Close': 'AdjClose',
            'Volume': 'Volume',
            'Dividends': 'Dividends',
            'Stock Splits': 'Stock_Splits'
        })

        historical_data['Volume'] = historical_data['Volume'].astype('int64')

        # Salvamento em CSV
        csv_file_name = f'{ticker_symbol}_{interval}_Historical_Data.csv'
        historical_data.to_csv(csv_file_name, index=False)
        print(f"Data for {ticker_symbol} at interval {interval} is collected and saved in {csv_file_name}.")
        
        return historical_data
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol} at interval {interval}: {e}")
        return None

def load_data_to_dolphindb(data, symbol, interval):
    """
    Uploads the given DataFrame to DolphinDB into a table specific to the interval.
    The table name convention is: stockdata_<interval>
    """
    try:
        # Upload the data to the server
        s.upload({'data': data})
        table_name = f"stockdata_{interval}"
        
        insert_script = f"""
        def insertData(data) {{
            t = loadTable("dfs://yfs", "{table_name}")
            t.append!(select 
                timestamp(Datetime) as Datetime, 
                Symbol, 
                Open, 
                High, 
                Low, 
                Close, 
                AdjClose,
                long(double(Volume)) as Volume,
                Dividends, 
                Stock_Splits 
            from data)
            return size(data)
        }}
        insertData(data)
        """
        result = s.run(insert_script)
        print(f"Data for {symbol} at interval {interval} loaded successfully into DolphinDB! Inserted {result} rows into {table_name}.")
        return result
    except Exception as e:
        print(f"Error loading data for {symbol} at interval {interval}: {e}")
        return 0

def remove_duplicates(table_name):
    """
    Remove duplicate records from the given DolphinDB table based on Datetime and Symbol.
    The duplicates are determined by groups having more than one record.
    Drops the table and recreates it with unique records.
    Returns:
        int: The number of duplicate groups found.
    """
    remove_script = f"""
    def removeDuplicates() {{
        stockData = loadTable("dfs://yfs", "{table_name}")
        
        // Find duplicates based on Datetime and Symbol
        duplicates = select Datetime, Symbol, count(*) as cnt from stockData 
                     group by Datetime, Symbol having count(*) > 1
        
        if (size(duplicates) > 0) {{
            // Select unique records using first() to pick the first occurrence for each group
            uniqueData = select Datetime, Symbol, 
                                 first(Open) as Open, first(High) as High, first(Low) as Low,
                                 first(Close) as Close, first(AdjClose) as AdjClose, first(Volume) as Volume, 
                                 first(Dividends) as Dividends, first(Stock_Splits) as Stock_Splits
                          from stockData
                          group by Datetime, Symbol
            
            // Drop the old table and create a new partitioned table with unique data
            db = database("dfs://yfs")
            db.dropTable("{table_name}")
            newTable = db.createPartitionedTable(uniqueData, "{table_name}", "Datetime")
            newTable.append!(uniqueData)
        }}
        
        return size(duplicates)
    }}
    removeDuplicates()
    """
    try:
        num_duplicates_removed = s.run(remove_script)
        if num_duplicates_removed == 0:
            print(f"No duplicates found in the {table_name} table.")
        else:
            print(f"Removed {num_duplicates_removed} duplicate entries from the {table_name} table.")
        return num_duplicates_removed
    except Exception as e:
        print(f"Error removing duplicates from {table_name}: {e}")
        return -1

def process_intervals(ticker_symbols, intervals):
    """
    For the given ticker symbols and a list of intervals,
    fetch, save, and load the historical data into a corresponding DolphinDB table for each interval.
    It also removes duplicates from each table after insertion.
    """
    for ticker_symbol in ticker_symbols:
        for interval in intervals:
            data = fetch_and_save_data(ticker_symbol, interval)
            if data is not None:
                rows_inserted = load_data_to_dolphindb(data, ticker_symbol, interval)
                print(f"Total rows inserted for {ticker_symbol} at interval {interval}: {rows_inserted}")
                table_name = f"stockdata_{interval}"
                remove_duplicates(table_name)
            time.sleep(1) #rate limt

# Main execution
if __name__ == "__main__":
    # Define the list of intervals to process
    intervals_list = ["90m", "60m", "15m", "5m"]
    
    # Get ticker symbols from the dict (using the "IBEE" key as in your example)
    ticker_symbols = TICKERS_DICT["TODOS"]
    ticker_symbols = add_sa_to_tickers(ticker_symbols)

    # Process each ticker symbol for all specified intervals
    process_intervals(ticker_symbols, intervals_list)

    # Optionally, verify the total rows for each interval table
    for interval in intervals_list:
        table_name = f"stockdata_{interval}"
        try:
            total_rows = s.run(f"select count(*) from loadTable('dfs://yfs', '{table_name}')")
            print(f"Total rows in {table_name} table: {total_rows}")
        except Exception as e:
            print(f"Error fetching total rows from {table_name}: {e}")

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
