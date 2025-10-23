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
from datetime import timezone, datetime
import time

# Properly handle imports whether the script is run directly or as a module
if __name__ == "__main__":
    from utils.supabase_handler import SupabaseHandler
else:
    from ..supabase_handler import SupabaseHandler

# Define the export directory path
EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export')
# Create export directory if it doesn't exist
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

def add_sa_to_tickers(tickers):
    return [ticker + '.SA' for ticker in tickers]

def store_data_in_supabase(df):
    """
    Store stock data in the Supabase yf_stocks_records table.
    Uses batch processing to avoid API limits.
    Handles conflicts by using insert() with on_conflict parameter.
    """
    try:
        # Initialize Supabase handler
        supabase_handler = SupabaseHandler()
        
        # Prepare data for insertion
        records = []
        for _, row in df.iterrows():
            record = {
                'datetime': int(row['Datetime']),
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
        
        # Insert or update in batches to avoid hitting API limits
        batch_size = 100
        total_records = len(records)
        upserted_count = 0
        
        for i in range(0, total_records, batch_size):
            batch = records[i:min(i + batch_size, total_records)]
            
            try:
                # Try the simplified approach - just use insert with 'ignore_duplicates'
                response = supabase_handler.supabase.table("yf_stocks_records").insert(
                    batch, 
                    count='exact'
                ).execute()
                
                if hasattr(response, 'data') and response.data:
                    upserted_count += len(response.data)
                    print(f"Inserted batch {i//batch_size + 1} with {len(response.data)} records")
                else:
                    print(f"Warning: Batch {i//batch_size + 1} may not have been inserted properly")
            except Exception as batch_error:
                if "duplicate key value violates unique constraint" in str(batch_error):
                    print(f"Batch {i//batch_size + 1} contains duplicates - will update records instead")
                    # Try inserting records individually with upsert
                    inserted_in_batch = 0
                    for record in batch:
                        try:
                            # Use RPC call to handle the upsert operation via a custom function
                            update_response = supabase_handler.supabase.rpc(
                                'upsert_yf_stocks_record',
                                {
                                    'p_datetime': record['datetime'],
                                    'p_datetime_str': record['datetime_str'],
                                    'p_symbol': record['symbol'], 
                                    'p_timeframe': record['timeframe'],
                                    'p_open': record['open'],
                                    'p_high': record['high'],
                                    'p_low': record['low'],
                                    'p_close': record['close'],
                                    'p_adj_close': record['adj_close'],
                                    'p_volume': record['volume'],
                                    'p_dividends': record['dividends'],
                                    'p_stock_splits': record['stock_splits'],
                                    'p_source': record['source']
                                }
                            ).execute()
                            
                            if hasattr(update_response, 'data') and update_response.data:
                                inserted_in_batch += 1
                        except Exception as record_error:
                            print(f"Error inserting individual record: {record_error}")
                    
                    upserted_count += inserted_in_batch
                    print(f"Individually updated {inserted_in_batch} records in batch {i//batch_size + 1}")
                else:
                    print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
        
        print(f"Successfully upserted {upserted_count} out of {total_records} records into Supabase.")
        return upserted_count > 0
    
    except Exception as e:
        print(f"Error storing data in Supabase: {e}")
        return False

def fetch_and_save_data(ticker_symbol, interval, save_csv=False):
    """
    Fetch historical stock data for a given ticker symbol and interval.
    Saves the data to a CSV file in the export directory and to Supabase.
    Returns the DataFrame.
    
    Args:
        ticker_symbol (str): The stock ticker symbol
        interval (str): Data interval (e.g., '1d', '1wk')
        save_csv (bool): Whether to save data to CSV file
    """
    try:
        stock_data = yf.Ticker(ticker_symbol)
        # Fetch historical data with the specified interval
        historical_data = stock_data.history(period="252d", interval=interval, auto_adjust=False)
        print(f"Fetching data for {ticker_symbol} at interval {interval}")
        
        if historical_data.empty:
            print(f"No data found for {ticker_symbol} at interval {interval}")
            return None
            
        # Process timestamp
        historical_data = historical_data.reset_index()
        historical_data['Date'] = pd.to_datetime(historical_data['Date'], utc=True)
        
        # Keep both formats - millisecond timestamp and human-readable string
        historical_data['Datetime'] = historical_data['Date'].astype('int64') // 10**6
        historical_data['Datetime_str'] = historical_data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        historical_data.drop(columns=['Date'], inplace=True)

        # Setup columns
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
            historical_data.to_csv(csv_path, index=False)
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

# Main execution
if __name__ == "__main__":
    # Define if CSV files should be saved locally
    save_csv_locally = False
    
    # Define the list of intervals to process
    intervals_list = ["1d"]
    
    # Get ticker symbols from the dict
    ticker_symbols = TICKERS_DICT["IBOV"]
    
    # Apply .SA suffix for Brazilian stocks
    ticker_symbols_with_sa = add_sa_to_tickers(ticker_symbols)
    
    # Process each ticker symbol for each interval
    for interval in intervals_list:
        print(f"Processing interval {interval}")
        for ticker in ticker_symbols_with_sa:
            df = fetch_and_save_data(ticker, interval, save_csv=save_csv_locally)
            # Add a small delay to avoid hitting rate limits
            time.sleep(1)
    
    print("All data processing complete.")


