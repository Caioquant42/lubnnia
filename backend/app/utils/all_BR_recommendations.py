import sys
import os
import json
import time
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# Add this block at the beginning of the file
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    from utils.dictionary import TICKERS_DICT
else:
    from .dictionary import TICKERS_DICT

tickers = TICKERS_DICT.get('TODOS', [])
def safe_get(dictionary, key, default=None):
    return dictionary.get(key, default)

def analyze_ibovlist(data):
    """
    Analyzes stocks in the Ibovespa index and ranks them by relevance.
    
    The analysis considers:
    - Number of analyst opinions (more is better)
    - % Distance to price targets (higher median and high distance is better)
    - Recommendation strength (closer to strong buy is better)
    """
    tickers = TICKERS_DICT.get('IBOV', [])
    
    # Filter the data to include only IBOV stocks
    ibov_data = {ticker: stock_data for ticker, stock_data in data.items() if ticker in tickers}
    
    # Create DataFrame with all data
    df = pd.DataFrame([
        {
            'ticker': ticker,
            'currentPrice': safe_get(stock_data, 'currentPrice'),
            'targetHighPrice': safe_get(stock_data, 'targetHighPrice'),
            'targetLowPrice': safe_get(stock_data, 'targetLowPrice'),
            'targetMeanPrice': safe_get(stock_data, 'targetMeanPrice'),
            'targetMedianPrice': safe_get(stock_data, 'targetMedianPrice'),
            'recommendationMean': safe_get(stock_data, 'recommendationMean'),
            'recommendationKey': safe_get(stock_data, 'recommendationKey'),
            'numberOfAnalystOpinions': safe_get(stock_data, 'numberOfAnalystOpinions'),
            'averageAnalystRating': safe_get(stock_data, 'averageAnalystRating'),
            '% Distance to Mean': safe_get(stock_data, '% Distance to Mean', 0),
            '% Distance to Median': safe_get(stock_data, '% Distance to Median', 0),
            '% Distance to Low': safe_get(stock_data, '% Distance to Low', 0),
            '% Distance to High': safe_get(stock_data, '% Distance to High', 0)
        }
        for ticker, stock_data in ibov_data.items()
    ])
    
    if len(df) == 0:
        return []

    # Convert to numeric and handle NaNs
    numeric_columns = [
        'currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 
        'targetMedianPrice', 'recommendationMean', 'numberOfAnalystOpinions',
        '% Distance to Mean', '% Distance to Median', '% Distance to Low', '% Distance to High'
    ]
    
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
      # Drop rows with missing essential data
    df = df.dropna(subset=[
        'currentPrice', 'numberOfAnalystOpinions'
    ])
    
    # Filter out tickers with only one analyst (require at least 2 analysts)
    df = df[df['numberOfAnalystOpinions'] > 1]
    
    if len(df) == 0:
        return []
    
    # Calculate additional metrics for scoring
    df['price_target_consensus'] = (
        (df['targetMedianPrice'] * 0.4) + 
        (df['targetHighPrice'] * 0.3) + 
        (df['targetMeanPrice'] * 0.3)
    )
    
    # Calculate return target consensus
    df['return_target_consensus'] = (
        (df['% Distance to Median'] * 0.4) + 
        (df['% Distance to High'] * 0.3) + 
        (df['% Distance to Mean'] * 0.3)
    )
    
    # Add inverse of recommendation mean (lower is better, closer to strong buy)
    # recommendationMean is usually 1-5 where 1 is strong buy
    df['recommendation_strength'] = 5 - df['recommendationMean']
    
    # Save original values before normalization
    df['original_analyst_opinions'] = df['numberOfAnalystOpinions'].copy()
    df['original_return_target_consensus'] = df['return_target_consensus'].copy()
    
    # Normalize metrics for scoring
    columns_to_normalize = [
        'numberOfAnalystOpinions', 
        'return_target_consensus',
        'recommendation_strength'
    ]
    
    # Use robust scaler to handle outliers
    if len(df) > 1:
        scaler = MinMaxScaler()
        df[columns_to_normalize] = scaler.fit_transform(
            df[columns_to_normalize]
        )
    
    # Calculate weighted combined score
    df['combined_score'] = (
        (df['numberOfAnalystOpinions'] * 0.25) +
        (df['return_target_consensus'] * 0.35) +
        (df['recommendation_strength'] * 0.15)
    )
    
    # Sort based on combined score
    sorted_tickers = df.sort_values(by='combined_score', ascending=False)
    
    # Add relevance ranking
    sorted_tickers['relevance'] = range(1, len(sorted_tickers) + 1)
    
    # Restore original values for the response
    sorted_tickers['numberOfAnalystOpinions'] = sorted_tickers['original_analyst_opinions']
    sorted_tickers['return_target_consensus'] = sorted_tickers['original_return_target_consensus']
    
    # Select only the columns we want to return
    result_columns = [
        'ticker', 'currentPrice', 'targetMedianPrice', 'targetHighPrice',
        'numberOfAnalystOpinions', 'recommendationMean', 'recommendationKey',
        '% Distance to Median', '% Distance to High', 'price_target_consensus',
        'return_target_consensus', 'combined_score', 'relevance'
    ]
    
    final_results = sorted_tickers[result_columns].copy()
    
    # Format numbers for better readability
    for col in ['recommendationMean', '% Distance to Median', '% Distance to High', 'return_target_consensus', 'combined_score']:
        if col in final_results.columns:
            final_results[col] = final_results[col].round(4)
    
    # Convert to dictionary
    result = final_results.to_dict(orient='records')
    
    return result

def analyze_strongbuy(data):
    """
    Analyzes stocks with 'strong_buy' recommendation and ranks them by relevance.
    
    The analysis considers:
    - Number of analyst opinions (more is better)
    - % Distance to price targets (higher median and high distance is better)
    - Price momentum (if available)
    - Trading volume (if available)
    """
    # Create DataFrame with all data
    df = pd.DataFrame([
        {
            'ticker': ticker,
            'currentPrice': safe_get(stock_data, 'currentPrice'),
            'targetHighPrice': safe_get(stock_data, 'targetHighPrice'),
            'targetLowPrice': safe_get(stock_data, 'targetLowPrice'),
            'targetMeanPrice': safe_get(stock_data, 'targetMeanPrice'),
            'targetMedianPrice': safe_get(stock_data, 'targetMedianPrice'),
            'recommendationMean': safe_get(stock_data, 'recommendationMean'),
            'recommendationKey': safe_get(stock_data, 'recommendationKey'),
            'numberOfAnalystOpinions': safe_get(stock_data, 'numberOfAnalystOpinions'),
            'averageAnalystRating': safe_get(stock_data, 'averageAnalystRating'),
            '% Distance to Mean': safe_get(stock_data, '% Distance to Mean', 0),
            '% Distance to Median': safe_get(stock_data, '% Distance to Median', 0),
            '% Distance to Low': safe_get(stock_data, '% Distance to Low', 0),
            '% Distance to High': safe_get(stock_data, '% Distance to High', 0)
        }
        for ticker, stock_data in data.items()
    ])

    # Filter for strong buy stocks
    strong_buy_assets = df[df['recommendationKey'] == 'strong_buy'].copy()
    
    if len(strong_buy_assets) == 0:
        return []

    # Convert to numeric and handle NaNs
    numeric_columns = [
        'currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 
        'targetMedianPrice', 'recommendationMean', 'numberOfAnalystOpinions',
        '% Distance to Mean', '% Distance to Median', '% Distance to Low', '% Distance to High'
    ]
    
    for col in numeric_columns:
        strong_buy_assets[col] = pd.to_numeric(strong_buy_assets[col], errors='coerce')
      # Drop rows with missing essential data
    strong_buy_assets = strong_buy_assets.dropna(subset=[
        'currentPrice', 'targetMedianPrice', 'numberOfAnalystOpinions'
    ])
    
    # Filter out tickers with only one analyst (require at least 2 analysts)
    strong_buy_assets = strong_buy_assets[strong_buy_assets['numberOfAnalystOpinions'] > 1]
    
    if len(strong_buy_assets) == 0:
        return []

    # Calculate additional metrics for scoring
    strong_buy_assets['price_target_consensus'] = (
        (strong_buy_assets['targetMedianPrice'] * 0.4) + 
        (strong_buy_assets['targetHighPrice'] * 0.3) + 
        (strong_buy_assets['targetMeanPrice'] * 0.3)
    )
    
    # Calculate additional metrics for scoring
    strong_buy_assets['return_target_consensus'] = (
        (strong_buy_assets['% Distance to Median'] * 0.4) + 
        (strong_buy_assets['% Distance to High'] * 0.3) + 
        (strong_buy_assets['% Distance to Mean'] * 0.3)
    )
    # recommendationMean is usually 1-5 where 1 is strong buy
    strong_buy_assets['recommendation_strength'] = 5 - strong_buy_assets['recommendationMean']
        
    # Filter out negative price consensus targets (expected to decrease)
    strong_buy_assets = strong_buy_assets[strong_buy_assets['return_target_consensus'] > 0]
    
    # Save original values before normalization
    strong_buy_assets['original_analyst_opinions'] = strong_buy_assets['numberOfAnalystOpinions'].copy()
    strong_buy_assets['original_return_target_consensus'] = strong_buy_assets['return_target_consensus'].copy()
   
    
    # Normalize metrics for scoring
    columns_to_normalize = [
        'numberOfAnalystOpinions', 
        'return_target_consensus',
        'recommendation_strength'
    ]
    
    # Use robust scaler to handle outliers
    if len(strong_buy_assets) > 1:
        scaler = MinMaxScaler()
        strong_buy_assets[columns_to_normalize] = scaler.fit_transform(
            strong_buy_assets[columns_to_normalize]
        )
    
    # Calculate weighted combined score
    strong_buy_assets['combined_score'] = (
        (strong_buy_assets['numberOfAnalystOpinions'] * 0.25) +
        (strong_buy_assets['return_target_consensus'] * 0.35) +
        (strong_buy_assets['recommendation_strength'] * 0.15)  

    )
    
    # Sort based on combined score
    sorted_tickers = strong_buy_assets.sort_values(by='combined_score', ascending=False)
    
    # Add relevance ranking
    sorted_tickers['relevance'] = range(1, len(sorted_tickers) + 1)
    
    # Restore original values for the response
    sorted_tickers['numberOfAnalystOpinions'] = sorted_tickers['original_analyst_opinions']
    sorted_tickers['return_target_consensus'] = sorted_tickers['original_return_target_consensus']
    
    # Select only the columns we want to return
    result_columns = [
        'ticker', 'currentPrice', 'targetMedianPrice', 'targetHighPrice',
        'numberOfAnalystOpinions', '% Distance to Median', '% Distance to High', 'price_target_consensus', 
        'return_target_consensus', 'combined_score', 'relevance'
    ]
    
    final_results = sorted_tickers[result_columns].copy()
    
    # Format numbers for better readability
    for col in ['% Distance to Median', '% Distance to High', 'return_target_consensus', 'combined_score']:
        if col in final_results.columns:
            final_results[col] = final_results[col].round(4)
    
    # Convert to dictionary
    result = final_results.to_dict(orient='records')
    
    return result

def analyze_buy(data):
    """
    Analyzes stocks with 'buy' recommendation and ranks them by relevance.
    
    The analysis considers:
    - Number of analyst opinions (more is better)
    - % Distance to price targets (higher median and high distance is better)
    - Consensus strength (closer to strong buy is better)
    """
    # Create DataFrame with all data
    df = pd.DataFrame([
        {
            'ticker': ticker,
            'currentPrice': safe_get(stock_data, 'currentPrice'),
            'targetHighPrice': safe_get(stock_data, 'targetHighPrice'),
            'targetLowPrice': safe_get(stock_data, 'targetLowPrice'),
            'targetMeanPrice': safe_get(stock_data, 'targetMeanPrice'),
            'targetMedianPrice': safe_get(stock_data, 'targetMedianPrice'),
            'recommendationMean': safe_get(stock_data, 'recommendationMean'),
            'recommendationKey': safe_get(stock_data, 'recommendationKey'),
            'numberOfAnalystOpinions': safe_get(stock_data, 'numberOfAnalystOpinions'),
            'averageAnalystRating': safe_get(stock_data, 'averageAnalystRating'),
            '% Distance to Mean': safe_get(stock_data, '% Distance to Mean', 0),
            '% Distance to Median': safe_get(stock_data, '% Distance to Median', 0),
            '% Distance to Low': safe_get(stock_data, '% Distance to Low', 0),
            '% Distance to High': safe_get(stock_data, '% Distance to High', 0)
        }
        for ticker, stock_data in data.items()
    ])

    # Filter for buy stocks
    buy_assets = df[df['recommendationKey'] == 'buy'].copy()
    
    if len(buy_assets) == 0:
        return []

    # Convert to numeric and handle NaNs
    numeric_columns = [
        'currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 
        'targetMedianPrice', 'recommendationMean', 'numberOfAnalystOpinions',
        '% Distance to Mean', '% Distance to Median', '% Distance to Low', '% Distance to High'
    ]
    
    for col in numeric_columns:
        buy_assets[col] = pd.to_numeric(buy_assets[col], errors='coerce')
      # Drop rows with missing essential data
    buy_assets = buy_assets.dropna(subset=[
        'currentPrice', 'targetMedianPrice', 'numberOfAnalystOpinions'
    ])
    
    # Filter out tickers with only one analyst (require at least 2 analysts)
    buy_assets = buy_assets[buy_assets['numberOfAnalystOpinions'] > 1]
    
    if len(buy_assets) == 0:
        return []
    # Calculate additional metrics for scoring
    buy_assets['price_target_consensus'] = (
        (buy_assets['targetMedianPrice'] * 0.4) + 
        (buy_assets['targetHighPrice'] * 0.3) + 
        (buy_assets['targetMeanPrice'] * 0.3)
    )
    # Calculate additional metrics for scoring
    buy_assets['return_target_consensus'] = (
        (buy_assets['% Distance to Median'] * 0.4) + 
        (buy_assets['% Distance to High'] * 0.3) + 
        (buy_assets['% Distance to Mean'] * 0.3)
    )
    
    
    
    # Add inverse of recommendation mean (lower is better, closer to strong buy)
    # recommendationMean is usually 1-5 where 1 is strong buy
    buy_assets['recommendation_strength'] = 5 - buy_assets['recommendationMean']
    
    # Filter out negative price consensus targets (expected to decrease)
    buy_assets = buy_assets[buy_assets['return_target_consensus'] > 0]
    
    # Save original values before normalization
    buy_assets['original_analyst_opinions'] = buy_assets['numberOfAnalystOpinions'].copy()
    buy_assets['original_return_target_consensus'] = buy_assets['return_target_consensus'].copy()
    
    # Normalize metrics for scoring
    columns_to_normalize = [
        'numberOfAnalystOpinions', 
        'return_target_consensus',
        'recommendation_strength',
    ]
    
    # Use robust scaler to handle outliers
    if len(buy_assets) > 1:
        scaler = MinMaxScaler()
        buy_assets[columns_to_normalize] = scaler.fit_transform(
            buy_assets[columns_to_normalize]
        )
    
    # Calculate weighted combined score
    buy_assets['combined_score'] = (
        (buy_assets['numberOfAnalystOpinions'] * 0.25) +
        (buy_assets['return_target_consensus'] * 0.35) +
        (buy_assets['recommendation_strength'] * 0.15) 
    )
    
    # Sort based on combined score
    sorted_tickers = buy_assets.sort_values(by='combined_score', ascending=False)
    
    # Add relevance ranking
    sorted_tickers['relevance'] = range(1, len(sorted_tickers) + 1)
    
    # Restore original values for the response
    sorted_tickers['numberOfAnalystOpinions'] = sorted_tickers['original_analyst_opinions']
    sorted_tickers['return_target_consensus'] = sorted_tickers['original_return_target_consensus']
    
    # Select only the columns we want to return
    result_columns = [
        'ticker', 'currentPrice', 'targetMedianPrice', 'targetHighPrice',
        'numberOfAnalystOpinions', 'recommendationMean',
        '% Distance to Median', '% Distance to High', 'price_target_consensus',
        'return_target_consensus','combined_score', 'relevance'
    ]
    
    final_results = sorted_tickers[result_columns].copy()
    
    # Format numbers for better readability
    for col in ['recommendationMean', '% Distance to Median', '% Distance to High', 'return_target_consensus', 'combined_score']:
        if col in final_results.columns:
            final_results[col] = final_results[col].round(4)
    
    # Convert to dictionary
    result = final_results.to_dict(orient='records')
    
    return result

def get_recommendations_analysis(ticker=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(current_dir, "export")
    
    # Get the most recent file
    files = [f for f in os.listdir(export_dir) if f.startswith('all_BR_recommendations_') and f.endswith('.json')]
    if not files:
        print("No recommendations data files found.")
        return {}
    
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(export_dir, x)))
    json_file_path = os.path.join(export_dir, latest_file)
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            recommendations_data = json.load(json_file)
        
        # Return data for specific ticker if provided
        if (ticker):
            return {ticker: recommendations_data.get(ticker, {})}
        
        return recommendations_data
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {json_file_path}")
        return {}

        
class YData:
    def __init__(self, ticker_symbol, interval='1d', period='2d', world=False, start_date=None, end_date=None):
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
            if current_price is not None and current_price != 0:
                filtered_info['% Distance to Mean'] = ((filtered_info.get('targetMeanPrice', 0) - current_price) / current_price) 
                filtered_info['% Distance to Median'] = ((filtered_info.get('targetMedianPrice', 0) - current_price) / current_price) 
                filtered_info['% Distance to Low'] = ((filtered_info.get('targetLowPrice', 0) - current_price) / current_price) 
                filtered_info['% Distance to High'] = ((filtered_info.get('targetHighPrice', 0) - current_price) / current_price) 
            else:
                filtered_info['% Distance to Mean'] = None
                filtered_info['% Distance to Median'] = None
                filtered_info['% Distance to Low'] = None
                filtered_info['% Distance to High'] = None
            
            return filtered_info

        except Exception as e:
            print(f"Error retrieving fundamental data summary for {self.ticker}: {e}")
            return None

def save_all_fundamental_data_to_json(filename):
    all_data = {}
    for ticker in tickers:
        ydata = YData(ticker)
        ticker_data = ydata.get_fundamental_data_summary()
        if ticker_data:
            all_data[ticker] = ticker_data

        print(f"{ticker} loaded successfully")
        time.sleep(1)
    
    try:
        # Get the full path for the file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        export_dir = os.path.join(current_dir, 'export')
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'all_BR_recommendations.json'
        full_path = os.path.join(export_dir, filename)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        print(f"All Recommendations data summaries saved to {full_path}")
    
    except Exception as e:
        print(f"Error saving all Recommendations data summaries to {full_path}: {e}")





def main():
    filename = "all_BR_recommendations.json"
    save_all_fundamental_data_to_json(filename)
    print(f"Code last executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()