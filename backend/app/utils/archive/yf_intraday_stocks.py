#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import io
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(project_root)
sys.path.insert(0, project_root)
from dictionary import TICKERS_DICT
import yfinance as yf
import pandas as pd
from datetime import timezone, datetime, timedelta
import time
import glob

# Properly handle imports whether the script is run directly or as a module
if __name__ == "__main__":
    from utils.supabase_handler import SupabaseHandler
else:
    from .supabase_handler import SupabaseHandler

# Define the export directory path
EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export')
# Create export directory if it doesn't exist
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

def add_sa_to_tickers(tickers):
    return [ticker + '.SA' for ticker in tickers]

def store_data_in_supabase(df):
    """
    Store stock data in the Supabase yf_intraday_stocks_records table.
    Uses batch processing to avoid API limits.
    """
    try:
        # Initialize Supabase handler
        supabase_handler = SupabaseHandler()
        
        # Prepare data for insertion
        records = []
        for _, row in df.iterrows():
            record = {
                'datetime': int(row['Datetime_ms']),
                'datetime_str': row['Datetime_str'],
                'symbol': row['Symbol'],
                'timeframe': row['Timeframe'],
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'adj_close': float(row['AdjClose']),
                'volume': int(row['Volume']),
                'dividends': float(row['Dividends']) if pd.notna(row['Dividends']) else 0,
                'stock_splits': float(row['Stock_Splits']) if pd.notna(row['Stock_Splits']) else 0,
                'source': 'yfinance'
            }
            records.append(record)
        
        # Insert in batches to avoid hitting API limits
        batch_size = 100
        total_records = len(records)
        inserted_count = 0
        
        for i in range(0, total_records, batch_size):
            batch = records[i:min(i + batch_size, total_records)]
            
            try:
                response = supabase_handler.supabase.table("yf_intraday_stocks_records").insert(batch).execute()
                if hasattr(response, 'data') and response.data:
                    inserted_count += len(batch)
                    print(f"Inserted batch {i//batch_size + 1} with {len(batch)} records")
                else:
                    print(f"Warning: Batch {i//batch_size + 1} may not have been inserted properly")
            except Exception as batch_error:
                print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
        
        print(f"Successfully inserted {inserted_count} out of {total_records} records into Supabase.")
        return inserted_count > 0
    
    except Exception as e:
        print(f"Error storing data in Supabase: {e}")
        return False

def fetch_and_save_data(ticker_symbol, interval, period="20d", save_csv=False):
    """
    Fetch historical stock data for a given ticker symbol and interval.
    Saves the data to a CSV file in the export directory and to Supabase.
    Returns the DataFrame.
    
    Args:
        ticker_symbol (str): The stock ticker symbol
        interval (str): Data interval (e.g., '60m', '15m', '5m')
        period (str): Data period (default: "20d")
        save_csv (bool): Whether to save data to CSV file
    """
    try:
        stock_data = yf.Ticker(ticker_symbol)
        # Fetch historical data with the specified interval
        historical_data = stock_data.history(period=period, interval=interval, auto_adjust=False)
        print(f"Fetching data for {ticker_symbol} at interval {interval}")
        
        if historical_data.empty:
            print(f"No data found for {ticker_symbol} at interval {interval}")
            return None
            
        # Reset index to make datetime a column
        historical_data = historical_data.reset_index()
        
        # Convert datetime to UTC and then to milliseconds since epoch
        historical_data['Datetime'] = pd.to_datetime(historical_data['Datetime'], utc=True)
        # Save the datetime in milliseconds for database storage
        historical_data['Datetime_ms'] = historical_data['Datetime'].astype('int64') // 10**6
        # Create a human-readable datetime string
        historical_data['Datetime_str'] = historical_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Add Symbol column right after Datetime
        historical_data.insert(1, 'Symbol', ticker_symbol.replace('.SA', ''))
        # Add timeframe column
        historical_data['Timeframe'] = interval

        # Mapeamento e conversão de tipos
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
        csv_path = os.path.join(EXPORT_DIR, csv_file_name)
        
        if save_csv:
            # Keep the original Datetime for CSV export to maintain readability
            export_df = historical_data.copy()
            export_df.drop(columns=['Datetime_ms'], inplace=True)
            export_df.rename(columns={'Datetime_str': 'Datetime'}, inplace=True)
            export_df.to_csv(csv_path, index=False)
            print(f"Data for {ticker_symbol} at interval {interval} is collected and saved in {csv_path}.")
        else:
            print(f"Data for {ticker_symbol} at interval {interval} is collected (CSV export disabled).")
        
        # Store in Supabase database
        success = store_data_in_supabase(historical_data)
        
        if not success and save_csv:
            # Backup CSV to export directory if Supabase insertion failed
            print(f"Supabase insertion failed. CSV backup saved to {csv_path}")
        elif not success:
            print(f"Supabase insertion failed. CSV backup not saved (export disabled).")
        
        return historical_data
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol} at interval {interval}: {e}")
        return None

def process_intervals(ticker_symbols, intervals_list, period="20d", save_csv=False):
    """
    For the given ticker symbols and a list of intervals,
    fetch, save, and load the historical data into Supabase.
    
    Args:
        ticker_symbols (list): List of ticker symbols to process
        intervals_list (list): List of intervals to process
        period (str): Data period (default: "20d")
        save_csv (bool): Whether to save data to CSV files
    """
    for interval in intervals_list:
        print(f"\nProcessing interval {interval}")
        for ticker_symbol in ticker_symbols:
            data = fetch_and_save_data(ticker_symbol, interval, period, save_csv)
            if data is not None:
                print(f"Total rows fetched for {ticker_symbol} at interval {interval}: {len(data)}")
            time.sleep(1)  # Rate limit

def clean_csv_files():
    """Delete all CSV files in the export directory"""
    csv_files = glob.glob(os.path.join(EXPORT_DIR, "*.csv"))
    for file in csv_files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")
    print("CSV cleaning completed.")

# Main execution
if __name__ == "__main__":
    # Define if CSV files should be saved locally
    save_csv_locally = False
    
    # Define the list of intervals to process
    intervals_list = ["60m", "15m"]
    
    # Get ticker symbols from the dict
    ticker_symbols = TICKERS_DICT["IBOV"]  # Use TODOS to get all tickers
    
    # Apply .SA suffix for Brazilian stocks
    ticker_symbols_with_sa = add_sa_to_tickers(ticker_symbols)
    
    # Process all ticker symbols for all intervals
    process_intervals(ticker_symbols_with_sa, intervals_list, "20d", save_csv_locally)
    
    # Clean up CSV files if they were created
    if save_csv_locally:
        pass
        #clean_csv_files()
    
    print("Intraday data processing complete.")


