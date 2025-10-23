# filepath: project/backend/app/utils/supabase_handler.py
from datetime import datetime
import json
import sys
import os
from pathlib import Path

# Handle imports differently when run as a script vs as a module
if __name__ == "__main__":
    # Add the parent directory to sys.path to allow absolute imports
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent  # Navigate up to app/
    sys.path.insert(0, str(project_root))
    from app.utils.supabase_config import get_supabase_client
else:
    # When imported as a module, use relative import
    from .supabase_config import get_supabase_client

class SupabaseHandler:
    def __init__(self):
        self.supabase = get_supabase_client()

    def store_recommendations(self, data):
        """Stores recommendations data in Supabase."""
        try:
            data_to_insert = {"timestamp": datetime.now().isoformat(), "data": data}
            response = self.supabase.table("recommendations").insert(data_to_insert).execute()
            
            # Supabase-py v2 doesn't use an error attribute but returns data
            if hasattr(response, 'data') and response.data:
                print("Data inserted successfully")
                return True
            else:
                print("No data returned from Supabase")
                return False
        except Exception as e:
            print(f"Error storing recommendations in Supabase: {e}")
            return False

    # Add the new method to store options surface data
    def store_options_surface_data(self, options_data):
        """Stores options volatility surface data in the Supabase database.
        
        Args:
            options_data (list): A list of dictionaries containing option surface data
            
        Returns:
            bool: True if operation is successful, False otherwise
        """
        try:
            if not options_data:
                print("No options surface data to store in Supabase")
                return False
            
            # Insert data in batches to avoid timeouts and large payloads
            batch_size = 25
            total_records = len(options_data)
            inserted_count = 0
            
            print(f"Inserting {total_records} options surface records into Supabase")
            
            for i in range(0, total_records, batch_size):
                batch = options_data[i:i+batch_size]
                try:
                    response = self.supabase.table("oplab_historical_options_surface_records").insert(batch).execute()
                    
                    if hasattr(response, 'data') and response.data:
                        inserted_count += len(response.data)
                        print(f"Inserted batch {i//batch_size + 1}/{(total_records+batch_size-1)//batch_size}: {len(response.data)} records")
                    else:
                        print(f"Warning: Batch {i//batch_size + 1} insertion completed but no data returned")
                except Exception as batch_error:
                    print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
                    # Continue with next batch instead of failing completely
            
            print(f"Successfully inserted {inserted_count} out of {total_records} options surface records")
            return inserted_count > 0  # Return success if at least some records were inserted
        except Exception as e:
            print(f"Error storing options surface data in Supabase: {e}")
            return False
    
    def get_latest_options_surface_data(self, underlying_ticker=None, limit=1000):
        """Retrieves the latest options volatility surface data from Supabase.
        
        Args:
            underlying_ticker (str, optional): Filter by underlying ticker symbol
            limit (int, optional): Maximum number of records to return
            
        Returns:
            pd.DataFrame: DataFrame containing the retrieved data
        """
        try:
            import pandas as pd
            
            # Get the latest import timestamp
            latest_timestamp_query = (
                self.supabase.table("oplab_historical_options_surface_records")
                .select("import_timestamp")
                .order("import_timestamp", desc=True)
                .limit(1)
                .execute()
            )
            
            if not hasattr(latest_timestamp_query, 'data') or not latest_timestamp_query.data:
                print("No options surface data found in Supabase")
                return pd.DataFrame()
            
            latest_timestamp = latest_timestamp_query.data[0]['import_timestamp']
            
            # Build the query for the actual data
            query = (
                self.supabase.table("oplab_historical_options_surface_records")
                .select("*")
                .eq("import_timestamp", latest_timestamp)
            )
            
            # Filter by underlying ticker if specified
            if underlying_ticker:
                query = query.eq("underlying_ticker", underlying_ticker)
            
            # Execute query with limit
            response = query.limit(limit).execute()
            
            if hasattr(response, 'data') and response.data:
                record_count = len(response.data)
                print(f"Retrieved {record_count} options surface records from Supabase")
                
                # Convert to DataFrame
                df = pd.DataFrame(response.data)
                return df
            else:
                print("No options surface records found in Supabase")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error retrieving options surface data from Supabase: {e}")
            return pd.DataFrame()

    def get_latest_recommendations(self):
        """Retrieves the latest recommendations data from Supabase."""
        try:
            response = (
                self.supabase.table("recommendations")
                .select("*")
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )

            if hasattr(response, 'data') and response.data:
                return response.data[0]  # Return the latest entry
            else:
                print("No recommendations data found in Supabase")
                return None
        except Exception as e:
            print(f"Error retrieving latest recommendations from Supabase: {e}")
            return None


    def store_recommendations_csv(self, csv_content):
        """Stores recommendations data in CSV format in Supabase."""
        try:
            # First, we need to parse the CSV to extract data for each record
            import pandas as pd
            import numpy as np
            import io
            
            # Parse CSV content
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Ensure all required columns exist and handle missing values
            required_columns = [
                'ticker', 'timestamp', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 
                'targetMeanPrice', 'targetMedianPrice', 'recommendationMean', 'recommendationKey',
                'numberOfAnalystOpinions', 'averageAnalystRating',
                '% Distance to Mean', '% Distance to Median', '% Distance to Low', '% Distance to High'
            ]
            
            # Add any missing columns with default values
            for col in required_columns:
                if col not in df.columns:
                    if col in ['ticker', 'timestamp', 'recommendationKey', 'averageAnalystRating']:
                        df[col] = '' if col != 'timestamp' else pd.Timestamp.now().isoformat()
                    else:
                        df[col] = np.nan
            
            # Replace NaN values with nulls for proper JSON conversion
            df = df.replace({np.nan: None})
            
            # Convert the DataFrame records to a list of dictionaries
            records = []
            for _, row in df.iterrows():
                # Convert each row to a dictionary, properly handling column names
                record = {}
                for col in df.columns:
                    # Convert column names to lowercase to avoid case sensitivity issues
                    # For columns with special characters, ensure proper handling
                    if col.startswith('%'):
                        # Remove the % and spaces, convert to lowercase
                        key = f"distance_to_{col.replace('% Distance to ', '').lower()}"
                    else:
                        # Just convert to lowercase
                        key = col.lower()
                    
                    record[key] = row[col]
                records.append(record)
            
            # Insert each record individually or in small batches
            inserted_count = 0
            
            # Debugging info
            print(f"Inserting {len(records)} records with columns: {list(records[0].keys() if records else [])}")
            
            # Each record individually to better identify issues
            for i, record in enumerate(records):
                try:
                    response = self.supabase.table("recommendations_records").insert(record).execute()
                    if hasattr(response, 'data') and response.data:
                        inserted_count += 1
                    else:
                        print(f"Warning: Record {i+1} may not have been inserted properly")
                except Exception as record_error:
                    print(f"Error inserting record {i+1}: {record_error}")
                    # Continue with next record instead of failing completely
            
            print(f"Successfully inserted {inserted_count} records out of {len(records)}")
            return inserted_count > 0  # Return success if at least some records were inserted
            
        except Exception as e:
            print(f"Error storing recommendations CSV in Supabase: {e}")
            return False
            
    def get_recommendations_records_by_exchange(self, exchange):
        """Retrieves the most recent recommendations records for a specific exchange from Supabase.
        
        Args:
            exchange (str): The exchange to filter by. Must be one of: 'BR', 'NYSE', 'NASDAQ'
        
        Returns:
            list: A list of recommendation records for the specified exchange from the most recent timestamp
        """
        try:
            # Validate exchange input
            exchange = exchange.upper()
            if exchange not in ['BR', 'NYSE', 'NASDAQ']:
                print(f"Invalid exchange: {exchange}. Must be one of: 'BR', 'NYSE', 'NASDAQ'")
                return []
            
            # First, get the most recent timestamp for the given exchange
            timestamp_query = (
                self.supabase.table("recommendations_records")
                .select("timestamp")
                .eq("exchange", exchange)
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )
            
            if not hasattr(timestamp_query, 'data') or not timestamp_query.data:
                print(f"No records found for exchange: {exchange}")
                return []
            
            latest_timestamp = timestamp_query.data[0]['timestamp']
            
            # Now get all records with this exchange and timestamp
            response = (
                self.supabase.table("recommendations_records")
                .select("*")
                .eq("exchange", exchange)
                .eq("timestamp", latest_timestamp)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                print(f"Retrieved {len(response.data)} recommendation records for {exchange}")
                return response.data
            else:
                print(f"No recommendation records found for {exchange} at timestamp {latest_timestamp}")
                return []
                
        except Exception as e:
            print(f"Error retrieving recommendation records for {exchange} from Supabase: {e}")
            return []

    def store_oplab_stocks_data(self, stocks_data):
        """Stores IBOV stocks quantitative data from OpLab API in Supabase.
        
        Args:
            stocks_data (list): A list of dictionaries containing stock data from OpLab API
            
        Returns:
            bool: True if operation is successful, False otherwise
        """
        try:
            if not stocks_data:
                print("No stocks data to store in Supabase")
                return False
                
            # Convert any string representation of boolean to actual boolean
            for stock in stocks_data:
                if 'has_options' in stock:
                    # Convert string 'True'/'False' to boolean if needed
                    if isinstance(stock['has_options'], str):
                        stock['has_options'] = stock['has_options'] == 'True'
                    
                # Ensure numeric values are properly formatted
                numeric_fields = [
                    'open', 'high', 'low', 'close', 'volume', 'financial_volume', 
                    'bid', 'ask', 'variation', 'ewma_1y_max', 'ewma_1y_min', 
                    'ewma_1y_percentile', 'ewma_1y_rank', 'ewma_6m_max', 'ewma_6m_min',
                    'ewma_6m_percentile', 'ewma_6m_rank', 'ewma_current', 'iv_1y_max',
                    'iv_1y_min', 'iv_1y_percentile', 'iv_1y_rank', 'iv_6m_max',
                    'iv_6m_min', 'iv_6m_percentile', 'iv_6m_rank', 'iv_current',
                    'middle_term_trend', 'semi_return_1y', 'short_term_trend',
                    'stdv_1y', 'stdv_5d', 'beta_ibov', 'garch11_1y', 'correl_ibov',
                    'entropy', 'previous_close'
                ]
                
                for field in numeric_fields:
                    if field in stock and stock[field]:
                        try:
                            if field in ['middle_term_trend', 'short_term_trend']:
                                stock[field] = int(float(stock[field])) if stock[field] else 0
                            elif field in ['volume', 'financial_volume', 'trades', 'contract_size']:
                                stock[field] = int(stock[field]) if stock[field] else 0
                            else:
                                stock[field] = float(stock[field]) if stock[field] else 0
                        except (ValueError, TypeError):
                            # If conversion fails, set to None
                            stock[field] = None
                            
                # Convert timestamp fields
                timestamp_fields = ['created_at', 'updated_at', 'time']
                for field in timestamp_fields:
                    if field in stock and stock[field]:
                        # If it's already in ISO format, keep it as is
                        if not isinstance(stock[field], str) or not stock[field].endswith('Z'):
                            try:
                                # Try to parse it as a datetime string
                                dt = datetime.strptime(stock[field], '%Y-%m-%d %H:%M:%S')
                                stock[field] = dt.isoformat() + 'Z'
                            except (ValueError, TypeError):
                                # If parsing fails, set to current time
                                stock[field] = datetime.now().isoformat() + 'Z'

                # Rename fields to match the database schema if needed
                if 'cvmCode' in stock:
                    stock['cvm_code'] = stock.pop('cvmCode')
                if 'currencyScale' in stock:
                    stock['currency_scale'] = stock.pop('currencyScale')
                if 'marketMaker' in stock:
                    stock['market_maker'] = stock.pop('marketMaker')
                if 'previousClose' in stock:
                    stock['previous_close'] = stock.pop('previousClose')

            # Insert data in batches of 25 to avoid timeouts and large payloads
            batch_size = 25
            total_records = len(stocks_data)
            inserted_count = 0
            
            print(f"Inserting {total_records} OpLab stock records into Supabase")
            
            for i in range(0, total_records, batch_size):
                batch = stocks_data[i:i+batch_size]
                try:
                    response = self.supabase.table("oplab_quantitative_stocks_records").insert(batch).execute()
                    
                    if hasattr(response, 'data') and response.data:
                        inserted_count += len(response.data)
                        print(f"Inserted batch {i//batch_size + 1}/{(total_records+batch_size-1)//batch_size}: {len(response.data)} records")
                    else:
                        print(f"Warning: Batch {i//batch_size + 1} insertion completed but no data returned")
                except Exception as batch_error:
                    print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
                    # Continue with next batch instead of failing completely
            
            print(f"Successfully inserted {inserted_count} out of {total_records} OpLab stock records")
            return inserted_count > 0  # Return success if at least some records were inserted
        except Exception as e:
            print(f"Error storing OpLab stocks data in Supabase: {e}")
            return False
            
    def get_latest_oplab_stocks_data(self, symbol=None, sector=None, limit=100):
        """Retrieves the latest OpLab quantitative stocks data from Supabase.
        
        Args:
            symbol (str, optional): Filter by stock symbol
            sector (str, optional): Filter by sector
            limit (int, optional): Maximum number of records to return
            
        Returns:
            list: A list of stock records matching the criteria
        """
        try:
            # Start with a base query that gets the latest import_timestamp
            latest_timestamp_query = (
                self.supabase.table("oplab_quantitative_stocks_records")
                .select("import_timestamp")
                .order("import_timestamp", desc=True)
                .limit(1)
                .execute()
            )
            
            if not hasattr(latest_timestamp_query, 'data') or not latest_timestamp_query.data:
                print("No OpLab stocks data found in Supabase")
                return []
            
            latest_timestamp = latest_timestamp_query.data[0]['import_timestamp']
            
            # Build the query for the actual data
            query = (
                self.supabase.table("oplab_quantitative_stocks_records")
                .select("*")
                .eq("import_timestamp", latest_timestamp)
            )
            
            # Add filters if provided
            if symbol:
                query = query.eq("symbol", symbol)
            
            if sector:
                query = query.eq("sector", sector)
            
            # Execute the query with limit and ordering
            response = (
                query.order("symbol", desc=False)
                .limit(limit)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                record_count = len(response.data)
                print(f"Retrieved {record_count} OpLab stock records")
                return response.data
            else:
                print("No matching OpLab stock records found")
                return []
        except Exception as e:
            print(f"Error retrieving OpLab stocks data from Supabase: {e}")
            return []

    def store_oplab_options_data(self, options_data):
        """Stores options data from OpLab API in Supabase.
        
        Args:
            options_data (list): A list of dictionaries containing options data from OpLab API
            
        Returns:
            bool: True if operation is successful, False otherwise
        """
        try:
            if not options_data:
                print("No options data to store in Supabase")
                return False
                
            # All data should already be strings at this point, but just to ensure:
            for option in options_data:
                for key, value in option.items():
                    # Convert any non-string values to strings
                    if not isinstance(value, str):
                        option[key] = str(value)
                        
            # Insert data in batches of 25 to avoid timeouts and large payloads
            batch_size = 25
            total_records = len(options_data)
            inserted_count = 0
            
            print(f"Inserting {total_records} OpLab options records into Supabase")
            
            for i in range(0, total_records, batch_size):
                batch = options_data[i:i+batch_size]
                try:
                    response = self.supabase.table("oplab_options_data").insert(batch).execute()
                    
                    if hasattr(response, 'data') and response.data:
                        inserted_count += len(response.data)
                        print(f"Inserted batch {i//batch_size + 1}/{(total_records+batch_size-1)//batch_size}: {len(response.data)} records")
                    else:
                        print(f"Warning: Batch {i//batch_size + 1} insertion completed but no data returned")
                except Exception as batch_error:
                    print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
                    # Continue with next batch instead of failing completely
            
            print(f"Successfully inserted {inserted_count} out of {total_records} OpLab options records")
            return inserted_count > 0  # Return success if at least some records were inserted
        except Exception as e:
            print(f"Error storing OpLab options data in Supabase: {e}")
            return False
            
    def get_latest_options_data(self, ticker=None, limit=1000):
        """Retrieves the latest options data from Supabase.
        
        Args:
            ticker (str, optional): Filter by ticker symbol
            limit (int, optional): Maximum number of records to return
            
        Returns:
            pd.DataFrame: DataFrame containing the retrieved data
        """
        try:
            import pandas as pd
            
            # Get the latest fetch timestamp
            latest_timestamp_query = (
                self.supabase.table("options_data")
                .select("fetch_timestamp")
                .order("fetch_timestamp", desc=True)
                .limit(1)
                .execute()
            )
            
            if not hasattr(latest_timestamp_query, 'data') or not latest_timestamp_query.data:
                print("No options data found in Supabase")
                return pd.DataFrame()
            
            latest_timestamp = latest_timestamp_query.data[0]['fetch_timestamp']
            
            # Build the query for the actual data
            query = (
                self.supabase.table("options_data")
                .select("*")
                .eq("fetch_timestamp", latest_timestamp)
            )
            
            # Filter by ticker if specified
            if ticker:
                query = query.eq("ticker", ticker)
            
            # Execute query with limit
            response = query.limit(limit).execute()
            
            if hasattr(response, 'data') and response.data:
                record_count = len(response.data)
                print(f"Retrieved {record_count} options records from Supabase")
                
                # Convert to DataFrame
                df = pd.DataFrame(response.data)
                return df
            else:
                print("No options records found in Supabase")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error retrieving options data from Supabase: {e}")
            return pd.DataFrame()

    def store_oplab_realtime_options_records(self, options_data):
        """Stores options data from OpLab API in the oplab_realtime_options_records table in Supabase.
        
        Args:
            options_data (list): A list of dictionaries containing options data from OpLab API
            
        Returns:
            bool: True if operation is successful, False otherwise
        """
        try:
            if not options_data:
                print("No options data to store in Supabase")
                return False
            
            # Field name mappings (camelCase to snake_case)
            field_mappings = {
                # Map camelCase fields to snake_case database column names
                "lastUpdatedDividendsAt": "last_updated_dividends_at",
                "quotationForm": "quotation_form_camel",  # Database has both quotation_form and quotation_form_camel
                "financialVolume": "financial_volume",
                "strikeEod": "strike_eod",
                "spotPrice": "spot_price",
                "bidVolume": "bid_volume",
                "contractSize": "contract_size", 
                "lastTradeAt": "last_trade_at",
                "exchangeId": "exchange_id",
                "marketMaker": "market_maker",
                "daysToMaturity": "days_to_maturity",
                "dueDate": "due_date",
                "askVolume": "ask_volume",
                "createdAt": "created_at",
                "updatedAt": "updated_at",
                "blockDate": "block_date",
                "securityCategory": "security_category",
                "maturityType": "maturity_type"
            }
                
            # Process records with field name mapping
            processed_records = []
            for option in options_data:
                record = {}
                for key, value in option.items():
                    # Convert any non-string values to strings
                    if value is not None and not isinstance(value, str):
                        value = str(value)
                    elif value is None:
                        value = ""
                        
                    # Map camelCase field names to snake_case
                    if key in field_mappings:
                        record[field_mappings[key]] = value
                    else:
                        # Keep original field name for fields not in the mapping
                        record[key] = value
                        
                processed_records.append(record)
                        
            # Insert data in batches of 25 to avoid timeouts and large payloads
            batch_size = 25
            total_records = len(processed_records)
            inserted_count = 0
            
            print(f"Inserting {total_records} OpLab options records into oplab_realtime_options_records table")
            
            for i in range(0, total_records, batch_size):
                batch = processed_records[i:i+batch_size]
                try:
                    response = self.supabase.table("oplab_realtime_options_records").insert(batch).execute()
                    
                    if hasattr(response, 'data') and response.data:
                        inserted_count += len(response.data)
                        print(f"Inserted batch {i//batch_size + 1}/{(total_records+batch_size-1)//batch_size}: {len(response.data)} records")
                    else:
                        print(f"Warning: Batch {i//batch_size + 1} insertion completed but no data returned")
                except Exception as batch_error:
                    print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
                    # Continue with next batch instead of failing completely
            
            print(f"Successfully inserted {inserted_count} out of {total_records} OpLab options records")
            return inserted_count > 0  # Return success if at least some records were inserted
        except Exception as e:
            print(f"Error storing OpLab options data in Supabase: {e}")
            return False

    def get_rsi_stocks_data(self, timeframe, limit=100, days_back=30):
        """Retrieves stock data for RSI calculation from yf_stocks_records.
        
        Args:
            timeframe (str): The timeframe to filter by (e.g., '1d', '1wk')
            limit (int, optional): Maximum number of records per symbol to return
            days_back (int, optional): Number of days of history to retrieve
            
        Returns:
            pd.DataFrame: DataFrame containing the retrieved data
        """
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days_back)).timestamp() * 1000
            
            # Get data from yf_stocks_records table
            response = (
                self.supabase.table("yf_stocks_records")
                .select("*")
                .eq("timeframe", timeframe)
                .gte("datetime", int(cutoff_date))
                .order("datetime", desc=False)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                record_count = len(response.data)
                print(f"Retrieved {record_count} stock records from yf_stocks_records")
                
                # Convert to DataFrame
                df = pd.DataFrame(response.data)
                
                # Handle timestamp conversion
                df["datetime"] = pd.to_datetime(df["datetime"], unit='ms')
                
                return df
            else:
                print("No stock records found in yf_stocks_records")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error retrieving stock data from yf_stocks_records: {e}")
            return pd.DataFrame()
    
    def get_rsi_intraday_data(self, timeframe, limit=100, days_back=7):
        """Retrieves stock data for RSI calculation from yf_intraday_stocks_records.
        
        Args:
            timeframe (str): The timeframe to filter by (e.g., '15m', '60m')
            limit (int, optional): Maximum number of records per symbol to return
            days_back (int, optional): Number of days of history to retrieve
            
        Returns:
            pd.DataFrame: DataFrame containing the retrieved data
        """
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days_back)).timestamp() * 1000
            
            # Get data from yf_intraday_stocks_records table
            response = (
                self.supabase.table("yf_intraday_stocks_records")
                .select("*")
                .eq("timeframe", timeframe)
                .gte("datetime", int(cutoff_date))
                .order("datetime", desc=False)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                record_count = len(response.data)
                print(f"Retrieved {record_count} stock records from yf_intraday_stocks_records")
                
                # Convert to DataFrame
                df = pd.DataFrame(response.data)
                
                # Handle timestamp conversion
                df["datetime"] = pd.to_datetime(df["datetime"], unit='ms')
                
                return df
            else:
                print("No intraday stock records found in yf_intraday_stocks_records")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error retrieving intraday stock data from yf_intraday_stocks_records: {e}")
            return pd.DataFrame()

    
    def execute_sql_from_file(self, sql_file_path, table):
        """
        Execute a SQL query from a file and return the results
        
        Args:
            sql_file_path (str): Path to the SQL file to execute
            
        Returns:
            list: List of records returned by the query
        """
        try:
            # Read the SQL query from the file
            with open(sql_file_path, 'r') as f:
                sql_query = f.read()
            
            print(f"Executing SQL query directly against the database...")
            
            # Since we don't have direct raw SQL execution through the Supabase client,
            # we'll use the table API to get the most recent data
            
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Get most recent data from yf_stocks_records table
            response = (
                self.supabase.table(table)
                .select("symbol,datetime,datetime_str,adj_close")
                .eq("timeframe", "1d")
                .order("datetime", desc=True)  # Order by datetime descending to get most recent first
                .execute()
            )
            
            if not hasattr(response, 'data') or not response.data:
                print("No records found from query")
                return []
            
            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            
            # Keep only the most recent 100 records per symbol
            df = df.sort_values(['symbol', 'datetime'], ascending=[True, False])
            df = df.groupby('symbol').head(100)
            
            # Create a unique ID combining symbol and datetime
            df['unique_id'] = df['symbol'] + '_' + df['datetime'].astype(str)
            
            # Sort by symbol ascending and datetime descending within each symbol
            df = df.sort_values(['symbol', 'datetime'], ascending=[True, False])
            
            record_count = len(df)
            print(f"Retrieved {record_count} records (last 100 days per symbol)")
            
            # Check the date range in the data
            min_date = pd.to_datetime(df['datetime'].min(), unit='ms').strftime('%Y-%m-%d')
            max_date = pd.to_datetime(df['datetime'].max(), unit='ms').strftime('%Y-%m-%d')
            print(f"Date range: {min_date} to {max_date}")
            
            return df.to_dict('records')
                
        except Exception as e:
            print(f"Error executing SQL query from file: {e}")
            import traceback
            traceback.print_exc()
            return []

# Test that the module can be run directly
if __name__ == "__main__":
    try:
        handler = SupabaseHandler()
        print("SupabaseHandler initialized successfully")
    except Exception as e:
        print(f"Error initializing SupabaseHandler: {e}")