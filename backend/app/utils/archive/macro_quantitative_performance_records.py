import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import sys
import json

# Add the parent directory to sys.path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.utils.supabase_config import get_supabase_client

# Function to scrape CDI data
def scrape_cdi_data():
    url = "https://www.dadosdemercado.com.br/indices/cdi?form=MG0AV3"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', id='index-values')
    
    cdi_data = {}
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        year = columns[0].text.strip()
        monthly_data = {}
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for i, month in enumerate(months):
            value = columns[i+1].get('data-value')
            if value and value != 'None':
                monthly_data[month] = float(value)
        
        cdi_data[year] = monthly_data
    
    return cdi_data

# Function to fetch data from yfinance
def fetch_yfinance_data(ticker, start_date, end_date):
    data = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1mo")
    
    # Convert the index to the end of month dates in YYYY-MM-DD format
    result = {}
    for date, value in data['Close'].items():
        # Convert timestamp to datetime and format it as YYYY-MM-DD
        date_str = date.strftime('%Y-%m-%d')
        result[date_str] = value
    
    return result

def transform_cdi_data(cdi_data):
    transformed_data = {}
    month_map = {
        'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04', 'Mai': '05', 'Jun': '06',
        'Jul': '07', 'Ago': '08', 'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
    }

    # Create a list of tuples (date, value) for sorting
    data_list = []
    for year, months in cdi_data.items():
        for month, value in months.items():
            month_num = month_map[month]
            date = f"{year}-{month_num}-01"
            last_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            date_str = last_day.strftime("%Y-%m-%d")
            data_list.append((date_str, value))

    # Sort the list by date
    data_list.sort(key=lambda x: x[0])

    # Insert the sorted data into the dictionary
    for date_str, value in data_list:
        transformed_data[date_str] = value

    return transformed_data

def get_cumulative_performance():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "export", "cumulative_performance_data.json")
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return {}
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return {}

def save_to_supabase(df):
    """Saves the cumulative performance data to Supabase."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Convert dataframe to list of records for insertion
        records = []
        for date_str, row in df.iterrows():
            record = {
                'date': date_str.strftime('%Y-%m-%d'),
                'cdi': float(row['CDI']) if pd.notnull(row['CDI']) else None,
                'sp500': float(row['SP500']) if pd.notnull(row['SP500']) else None,
                'gold': float(row['Gold']) if pd.notnull(row['Gold']) else None,
                'usdbrl': float(row['USDBRL']) if pd.notnull(row['USDBRL']) else None,
                'ibov': float(row['IBOV']) if pd.notnull(row['IBOV']) else None
            }
            records.append(record)
        
        # Insert records in batches to avoid timeouts
        batch_size = 50
        total_records = len(records)
        inserted_count = 0
        
        print(f"Saving {total_records} records to Supabase table 'macro_quantitative_performance_records'")
        
        # Delete all existing records to avoid duplicates
        supabase.table("macro_quantitative_performance_records").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # Insert in batches
        for i in range(0, total_records, batch_size):
            batch = records[i:i+batch_size]
            try:
                response = supabase.table("macro_quantitative_performance_records").insert(batch).execute()
                
                if hasattr(response, 'data') and response.data:
                    inserted_count += len(response.data)
                    print(f"Inserted batch {i//batch_size + 1}/{(total_records+batch_size-1)//batch_size}: {len(response.data)} records")
                else:
                    print(f"Warning: Batch {i//batch_size + 1} insertion completed but no data returned")
            except Exception as batch_error:
                print(f"Error inserting batch {i//batch_size + 1}: {batch_error}")
        
        print(f"Successfully inserted {inserted_count} out of {total_records} records to Supabase")
        return inserted_count > 0  # Return success if at least some records were inserted
    except Exception as e:
        print(f"Error saving data to Supabase: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    # Scrape CDI data
    cdi_data = scrape_cdi_data()
    
    # Transform CDI data
    transformed_cdi_data = transform_cdi_data(cdi_data)
    
    # Set date range for yfinance data (past 25 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=25*365)
    
    # Fetch yfinance data
    sp500_data = fetch_yfinance_data("^GSPC", start_date, end_date)
    gold_data = fetch_yfinance_data("GC=F", start_date, end_date)
    brlusd_data = fetch_yfinance_data("USDBRL=X", start_date, end_date)
    ibov_data = fetch_yfinance_data("^BVSP", start_date, end_date)
    
    # Create DataFrames for each asset
    df_cdi = pd.DataFrame.from_dict(transformed_cdi_data, orient='index', columns=['CDI'])
    df_sp500 = pd.DataFrame.from_dict(sp500_data, orient='index', columns=['SP500'])
    df_gold = pd.DataFrame.from_dict(gold_data, orient='index', columns=['Gold'])
    df_brlusd = pd.DataFrame.from_dict(brlusd_data, orient='index', columns=['USDBRL'])
    df_ibov = pd.DataFrame.from_dict(ibov_data, orient='index', columns=['IBOV'])

    # Convert index to datetime for all dataframes
    df_cdi.index = pd.to_datetime(df_cdi.index)
    df_sp500.index = pd.to_datetime(df_sp500.index)
    df_gold.index = pd.to_datetime(df_gold.index)
    df_brlusd.index = pd.to_datetime(df_brlusd.index)
    df_ibov.index = pd.to_datetime(df_ibov.index)
    
    # Standardize to end of month for consistent dates
    def end_of_month(dt):
        next_month = dt.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)
        
    df_cdi.index = df_cdi.index.map(end_of_month)
    df_sp500.index = df_sp500.index.map(end_of_month)
    df_gold.index = df_gold.index.map(end_of_month)
    df_brlusd.index = df_brlusd.index.map(end_of_month)
    df_ibov.index = df_ibov.index.map(end_of_month)
    
    # Create date range for complete data (monthly from min to max date across all dataframes)
    min_date = min(df.index.min() for df in [df_cdi, df_sp500, df_gold, df_brlusd, df_ibov])
    max_date = max(df.index.max() for df in [df_cdi, df_sp500, df_gold, df_brlusd, df_ibov])
    
    # Create a complete date range with monthly frequency
    full_date_range = pd.date_range(start=min_date, end=max_date, freq='M')
    
    # Create an empty dataframe with the full date range as index
    df_combined = pd.DataFrame(index=full_date_range)
    
    # Join all dataframes
    df_combined = df_combined.join(df_cdi, how='left')
    df_combined = df_combined.join(df_sp500, how='left')
    df_combined = df_combined.join(df_gold, how='left')
    df_combined = df_combined.join(df_brlusd, how='left')
    df_combined = df_combined.join(df_ibov, how='left')
    
    # Filter out rows where all non-CDI values are missing (empty rows)
    asset_columns = ['SP500', 'Gold', 'USDBRL', 'IBOV']
    df_combined = df_combined[~df_combined[asset_columns].isna().all(axis=1)]
    
    # Apply date cutoff - only keep data from 2006-03-31 onwards
    cutoff_date = pd.to_datetime('2006-03-31')
    df_combined = df_combined[df_combined.index >= cutoff_date]
    
    # Fill missing values using interpolation (midpoint method)
    df_combined = df_combined.interpolate(method='linear', limit_direction='both')
    
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the export directory
    export_directory = os.path.join(current_directory, "export")
    
    # Create export directory if it doesn't exist
    os.makedirs(export_directory, exist_ok=True)
      # First save to Supabase
    save_success = save_to_supabase(df_combined)
    if save_success:
        print("Successfully saved data to Supabase")
    else:
        print("Warning: Failed to save data to Supabase")
    
    # Convert DataFrame to JSON format
    # Create the data structure for JSON
    json_data = {
        'metadata': {
            'date_range': {
                'start_date': df_combined.index.min().strftime('%Y-%m-%d'),
                'end_date': df_combined.index.max().strftime('%Y-%m-%d'),
                'total_periods': len(df_combined)
            },
            'available_assets': df_combined.columns.tolist(),
            'last_updated': datetime.now().isoformat()
        },
        'data': []
    }
    
    # Add the time series data
    for date_str, row in df_combined.iterrows():
        data_point = {
            'date': date_str.strftime('%Y-%m-%d')
        }
        # Add each asset's value
        for column in df_combined.columns:
            value = row[column]
            data_point[column] = float(value) if pd.notnull(value) else None
        
        json_data['data'].append(data_point)
    
    # Save the JSON data
    json_filename = os.path.join(export_directory, 'cumulative_performance_data.json')
    with open(json_filename, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"Data has been saved to {json_filename}")
    
    
    # Display stats about the data
    print(f"\nData statistics:")
    print(f"Date range: {df_combined.index.min().strftime('%Y-%m-%d')} to {df_combined.index.max().strftime('%Y-%m-%d')}")
    print(f"Total rows: {len(df_combined)}")
    print(f"Missing values after processing:")
    for column in df_combined.columns:
        missing = df_combined[column].isna().sum()
        print(f"  {column}: {missing} missing values ({missing/len(df_combined)*100:.1f}%)")