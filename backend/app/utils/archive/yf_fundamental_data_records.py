import sys
import os
import time
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    from app.utils.dictionary import TICKERS_DICT
    from app.utils.supabase_handler import SupabaseHandler
else:
    from .dictionary import TICKERS_DICT
    from .supabase_handler import SupabaseHandler

tickers = TICKERS_DICT.get('IBEE', [])

class YData:
    def __init__(self, ticker_symbol, interval='1d', period='5d', world=False, start_date=None, end_date=None):
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
                "industry", "sector", "auditRisk", "boardRisk", "compensationRisk",
                "shareHolderRightsRisk", "overallRisk", "governanceEpochDate",
                "executiveTeam", "maxAge", "priceHint", "previousClose", "open",
                "dayLow", "dayHigh", "regularMarketPreviousClose", "regularMarketOpen",
                "regularMarketDayLow", "regularMarketDayHigh", "dividendRate",
                "dividendYield", "exDividendDate", "payoutRatio", "fiveYearAvgDividendYield",
                "beta", "trailingPE", "forwardPE", "volume", "regularMarketVolume",
                "averageVolume", "averageVolume10days", "averageDailyVolume10Day",
                "bid", "ask", "bidSize", "askSize", "marketCap", "fiftyTwoWeekLow",
                "fiftyTwoWeekHigh", "priceToSalesTrailing12Months", "fiftyDayAverage",
                "twoHundredDayAverage", "trailingAnnualDividendRate", "trailingAnnualDividendYield",
                "currency", "tradeable", "enterpriseValue", "profitMargins", "floatShares",
                "sharesOutstanding", "heldPercentInsiders", "heldPercentInstitutions",
                "impliedSharesOutstanding", "bookValue", "priceToBook", "lastFiscalYearEnd",
                "nextFiscalYearEnd", "mostRecentQuarter", "earningsQuarterlyGrowth",
                "netIncomeToCommon", "trailingEps", "forwardEps", "lastSplitFactor",
                "lastSplitDate", "enterpriseToRevenue", "enterpriseToEbitda", "52WeekChange",
                "SandP52WeekChange", "lastDividendValue", "lastDividendDate", "quoteType",
                "currentPrice", "targetHighPrice", "targetLowPrice", "targetMeanPrice",
                "targetMedianPrice", "recommendationMean", "recommendationKey",
                "numberOfAnalystOpinions", "totalCash", "totalCashPerShare", "ebitda",
                "totalDebt", "quickRatio", "currentRatio", "totalRevenue", "debtToEquity",
                "revenuePerShare", "returnOnAssets", "returnOnEquity", "grossProfits",
                "freeCashflow", "operatingCashflow", "earningsGrowth", "revenueGrowth",
                "grossMargins", "ebitdaMargins", "operatingMargins", "financialCurrency",
                "symbol", "language", "region", "typeDisp", "quoteSourceName", "triggerable",
                "customPriceAlertConfidence", "marketState", "shortName", "longName",
                "hasPrePostMarketData", "firstTradeDateMilliseconds", "regularMarketChange",
                "regularMarketDayRange", "fullExchangeName", "averageDailyVolume3Month",
                "fiftyTwoWeekLowChange", "fiftyTwoWeekLowChangePercent", "fiftyTwoWeekRange",
                "fiftyTwoWeekHighChange", "fiftyTwoWeekHighChangePercent", "fiftyTwoWeekChangePercent",
                "earningsTimestamp", "earningsTimestampStart", "earningsTimestampEnd",
                "earningsCallTimestampStart", "earningsCallTimestampEnd", "isEarningsDateEstimate",
                "epsTrailingTwelveMonths", "epsForward", "epsCurrentYear", "priceEpsCurrentYear",
                "fiftyDayAverageChange", "fiftyDayAverageChangePercent", "twoHundredDayAverageChange",
                "twoHundredDayAverageChangePercent", "sourceInterval", "exchangeDataDelayedBy",
                "averageAnalystRating", "cryptoTradeable", "regularMarketChangePercent",
                "regularMarketPrice", "corporateActions", "regularMarketTime", "exchange",
                "esgPopulated", "trailingPegRatio"
            ]
            
            # Create a dictionary with only the desired fields
            filtered_info = {field: info.get(field) for field in desired_fields if field in info}
            
            return filtered_info

        except Exception as e:
            print(f"Error retrieving fundamental data summary for {self.ticker}: {e}")
            return None

def prepare_df_for_database(df):
    """
    Clean and prepare the DataFrame for database insertion by converting all values to strings
    """
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Convert column names to match the database schema
    # Convert all column names to lowercase for consistency
    df.columns = [col.lower() for col in df.columns]
    
    # Handle special column names with special characters
    if '52weekchange' in df.columns:
        df.rename(columns={'52weekchange': 'fiftytwoweekchange'}, inplace=True)
    if 'sandp52weekchange' in df.columns:
        df.rename(columns={'sandp52weekchange': 'sandpfiftytwoweekchange'}, inplace=True)
    
    # Remove any complex JSON columns that might cause issues
    columns_to_drop = ['executiveteam', 'corporateactions']
    for col in columns_to_drop:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
    
    # Convert ALL values to strings to avoid JSON incompatibilities
    for col in df.columns:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) or 
                                (isinstance(x, float) and (np.isnan(x) or np.isinf(x))) 
                                else str(x))
    
    return df

def save_fundamental_data_to_database(df):
    """
    Save the fundamental data to the database table as strings
    """
    try:
        # Prepare the DataFrame for database insertion with all values as strings
        df_for_db = prepare_df_for_database(df.copy())
        
        # Add timestamp to the data
        timestamp = datetime.now().isoformat()
        
        # Create a new dictionary with the timestamp field
        all_records = []
        
        for _, row in df_for_db.iterrows():
            # Convert row to dictionary
            record = row.to_dict()
            
            # Add timestamp field
            record['import_timestamp'] = timestamp
            
            # Make a final check to ensure all values are strings or None
            for key, value in record.items():
                if value is not None and not isinstance(value, str):
                    record[key] = str(value)
                    
            all_records.append(record)
        
        # Initialize Supabase handler
        supabase_handler = SupabaseHandler()
        
        # Insert records in small batches to prevent timeouts
        total_records = len(all_records)
        inserted_count = 0
        batch_size = 1  # Insert one at a time for maximum reliability
        
        for i in range(0, total_records, batch_size):
            batch = all_records[i:i+batch_size]
            
            for j, record in enumerate(batch):
                try:
                    response = supabase_handler.supabase.table("yf_fundamental_data_records").insert(record).execute()
                    
                    if hasattr(response, 'data') and response.data:
                        inserted_count += 1
                        print(f"Inserted record {i+j+1}/{total_records}")
                    else:
                        print(f"Warning: Record {i+j+1}/{total_records} may not have been inserted properly")
                except Exception as record_error:
                    print(f"Error inserting record {i+j+1}/{total_records}: {record_error}")
            
        print(f"Successfully inserted {inserted_count} out of {total_records} records into yf_fundamental_data_records table")
        return inserted_count > 0
        
    except Exception as e:
        print(f"Error saving data to database: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_all_fundamental_data_to_csv_and_db():
    """
    Get fundamental data and save to both CSV and database
    """
    all_data = []
    for ticker in tickers:
        ydata = YData(ticker)
        ticker_data = ydata.get_fundamental_data_summary()
        if ticker_data:
            # Add ticker as a field in the data
            ticker_data['ticker'] = ticker
            all_data.append(ticker_data)

        print(f"{ticker} loaded successfully")
        time.sleep(1)
    
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(all_data)
    
    # Always save to CSV first to ensure we have the data
    try:
        # Get the absolute path of the script directory
        current_directory = os.path.dirname(os.path.abspath(__file__))
        filename = 'all_fundamental_data_summaries.csv'
        
        # Ensure export directory exists
        export_dir = os.path.join(current_directory, 'export')
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        file_path = os.path.join(export_dir, filename)
        
        # Save as CSV
        df.to_csv(file_path, index=False)
        
        print(f"All fundamental data summaries saved to {file_path}")
        csv_success = True
    
    except Exception as e:
        print(f"Error saving all fundamental data summaries to CSV: {e}")
        csv_success = False
    
    # Try to save to database only after CSV is saved
    if csv_success:
        try:
            db_success = save_fundamental_data_to_database(df)
            if db_success:
                print("Successfully saved fundamental data to the database")
            else:
                print("Failed to save fundamental data to the database")
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    return csv_success

def get_fundamentalsummary_analysis():
    """
    Get fundamental data summary analysis from database or CSV fallback
    """
    try:
        # Try to get data from the database first
        supabase_handler = SupabaseHandler()
        response = (
            supabase_handler.supabase.table("yf_fundamental_data_records")
            .select("*")
            .order("import_timestamp", desc=True)
            .limit(1000)
            .execute()
        )
        
        if hasattr(response, 'data') and response.data:
            df = pd.DataFrame(response.data)
            print(f"Retrieved {len(df)} records from database")
            return df
            
        # If database query returns empty, fall back to CSV
        print("No data found in database, falling back to CSV...")
        raise Exception("No data in database")
        
    except Exception as e:
        print(f"Database retrieval failed: {e}, falling back to CSV")
        # Fall back to CSV file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, "export", "all_fundamental_data_summaries.csv")
        
        try:
            df = pd.read_csv(csv_file_path)
            print(f"Retrieved {len(df)} records from CSV")
            return df
        except FileNotFoundError:
            print(f"Error: File not found at {csv_file_path}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading CSV file {csv_file_path}: {e}")
            return pd.DataFrame()

def main():
    save_all_fundamental_data_to_csv_and_db()
    print(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()