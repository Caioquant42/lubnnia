from dolphindb import session
import numpy as np
import pandas as pd
import json
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from datetime import datetime, timedelta
import pyfolio as pf
import argparse
import sys
import traceback

STOCKS_DICT = {
    "stocks": ["PETR4", "VALE3", "BBAS3", "B3SA3", "JBSS3"], #substitue for the selected tickers on the react app
    "benchmark": ['BOVA11'],# this is fixed
    "period": [6, 12, 24, 36] # substitue for the selected radiobutton on the react app
}
def query_dolphindb():
    # Connect to the DolphinDB server
    s = session()
    s.connect("46.202.149.154", 8848, "admin", "123456")

    # Load the table from the distributed file system
    s.run('t = loadTable("dfs://yfs", "stockdata_1d")')

    # Execute the query to filter the data by Time and select specific columns
    # Use a proper datetime format with T separating the date and time
    ddb_data = s.run('select Datetime, Symbol, AdjClose from t where Datetime > 2021.01.01T03:00:00')
    

    return ddb_data
def optimize_portfolio(data, tickers, period):
    today = datetime.now()
    start_date = (today - timedelta(days=period * 30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Prepare the data
    df = data[data['Symbol'].isin(tickers)]
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
    df = df.pivot(index='Datetime', columns='Symbol', values='AdjClose')
    
    # Calculate returns
    returns = df.pct_change().dropna()
    
    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    
    # Maximum Sharpe Ratio Portfolio
    ef_max_sharpe = EfficientFrontier(mu, S)
    max_sharpe_weights = ef_max_sharpe.max_sharpe()
    max_sharpe_performance = ef_max_sharpe.portfolio_performance()
    
    # Calculate portfolio returns for Max Sharpe
    max_sharpe_returns = (returns * pd.Series(max_sharpe_weights)).sum(axis=1)
    max_sharpe_stats = pf.timeseries.perf_stats(max_sharpe_returns)
    
    # Minimum Variance Portfolio
    ef_min_variance = EfficientFrontier(mu, S)
    min_variance_weights = ef_min_variance.min_volatility()
    min_variance_performance = ef_min_variance.portfolio_performance()
    
    # Calculate portfolio returns for Min Variance
    min_variance_returns = (returns * pd.Series(min_variance_weights)).sum(axis=1)
    min_variance_stats = pf.timeseries.perf_stats(min_variance_returns)
    
    return (max_sharpe_weights, max_sharpe_performance, max_sharpe_stats, returns,
            min_variance_weights, min_variance_performance, min_variance_stats)

def calculate_and_save_cumulative_returns(weights, returns, file_name):
    # Calculate cumulative returns for the portfolio
    portfolio_returns = (returns * pd.Series(weights)).sum(axis=1)
    portfolio_cum_returns = (1 + portfolio_returns).cumprod() - 1
    
    # Calculate cumulative returns for individual assets
    asset_cum_returns = (1 + returns).cumprod() - 1
    
    # Combine portfolio and asset cumulative returns
    all_cum_returns = pd.concat([portfolio_cum_returns.rename('Portfolio'), asset_cum_returns], axis=1)
    
    # Save to CSV
    all_cum_returns.to_csv(file_name)
    print(f"Cumulative returns saved to {file_name}")

def calculate_cumulative_returns_with_benchmark(weights, returns, benchmark_returns):
    portfolio_returns = (returns * pd.Series(weights)).sum(axis=1)
    portfolio_cum_returns = (1 + portfolio_returns).cumprod() - 1
    benchmark_cum_returns = (1 + benchmark_returns).cumprod() - 1
    asset_cum_returns = (1 + returns).cumprod() - 1
    
    all_cum_returns = pd.concat([
        portfolio_cum_returns.rename('Portfolio'),
        benchmark_cum_returns.rename('Benchmark'),
        asset_cum_returns
    ], axis=1)
    
    # Convert index to strings and values to native Python types
    return {str(date): {col: float(val) for col, val in row.items()} 
            for date, row in all_cum_returns.iterrows()}
def run_optimization(stocks, period):
    try:
        tickers = stocks.split(',')

        print(f"Using tickers: {tickers}", file=sys.stderr)
        print(f"Using period: {period} months", file=sys.stderr)

        # Fetch data from DolphinDB
        ddb_data = query_dolphindb()

        benchmark_ticker = 'BOVA11'  # Fixed benchmark

        # Filter and calculate benchmark returns
        benchmark_data = ddb_data[ddb_data['Symbol'] == benchmark_ticker]
        benchmark_data['Datetime'] = pd.to_datetime(benchmark_data['Datetime'])
        benchmark_data = benchmark_data[(benchmark_data['Datetime'] >= (datetime.now() - timedelta(days=period * 30))) &
                                        (benchmark_data['Datetime'] <= datetime.now())]
        benchmark_prices = benchmark_data.pivot(index='Datetime', columns='Symbol', values='AdjClose')
        benchmark_returns = benchmark_prices.pct_change().dropna()

        # Optimize the portfolio
        (max_sharpe_weights, max_sharpe_performance, max_sharpe_stats, returns,
         min_variance_weights, min_variance_performance, min_variance_stats) = optimize_portfolio(ddb_data, tickers, period)

        # Calculate cumulative returns
        max_sharpe_cum_returns = calculate_cumulative_returns_with_benchmark(max_sharpe_weights, returns, benchmark_returns.squeeze())
        min_variance_cum_returns = calculate_cumulative_returns_with_benchmark(min_variance_weights, returns, benchmark_returns.squeeze())

        # Prepare data for JSON output
        tangency_data = {
            'weights': {k: float(v) for k, v in max_sharpe_weights.items()},
            'performance': {
                'expected_annual_return': float(max_sharpe_performance[0]),
                'annual_volatility': float(max_sharpe_performance[1]),
                'sharpe_ratio': float(max_sharpe_performance[2])
            },
            'stats': {k: float(v) if isinstance(v, (int, float, np.number)) else str(v) for k, v in max_sharpe_stats.to_dict().items()},
            'cumulative_returns': max_sharpe_cum_returns
        }

        min_variance_data = {
            'weights': {k: float(v) for k, v in min_variance_weights.items()},
            'performance': {
                'expected_annual_return': float(min_variance_performance[0]),
                'annual_volatility': float(min_variance_performance[1]),
                'sharpe_ratio': float(min_variance_performance[2])
            },
            'stats': {k: float(v) if isinstance(v, (int, float, np.number)) else str(v) for k, v in min_variance_stats.to_dict().items()},
            'cumulative_returns': min_variance_cum_returns
        }

        # Prepare the final results dictionary
        results = {
            'tangency_data': tangency_data,
            'min_variance_data': min_variance_data
        }

        return results

    except Exception as e:
        print(f"Error in opt.py: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise
if __name__ == "__main__":
    # This part is now only for testing purposes
    test_stocks = "PETR4,VALE3,ITUB4"
    test_period = 12
    results = run_optimization(test_stocks, test_period)
    print(json.dumps(results))



