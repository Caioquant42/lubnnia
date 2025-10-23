from dolphindb import session
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
import sys
import os
import traceback
from scipy.interpolate import CubicSpline
import argparse

STOCKS_DICT = {
    "stocks": ["PETR4", "VALE3"],
    "period": [6, 12],
}

def query_dolphindb():
    try:
        s = session()
        s.connect("46.202.149.154", 8848, "admin", "123456")
        s.run('t = loadTable("dfs://yfs", "stockdata_1d")')
        ddb_data = s.run('select Datetime, Symbol, AdjClose from t where Datetime > 2021.01.01T03:00:00')
        return pd.DataFrame(ddb_data)
    except Exception as e:
        print(f"Error querying DolphinDB: {str(e)}", file=sys.stderr)
        return None

def calculate_returns(data, tickers, period, iterations, time_steps):
    today = datetime.now()
    start_date = (today - timedelta(days=period * 30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    df = data[data['Symbol'].isin(tickers)]
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
    df = df.pivot(index='Datetime', columns='Symbol', values='AdjClose')

    results = {}
    for ticker in tickers:
        asset_df = df[[ticker]].copy()
        asset_df.columns = ['price']
        
        asset_df['simple_return'] = asset_df['price'].pct_change()
        asset_df['log_return'] = np.log(1 + asset_df['simple_return'])
        asset_df.dropna(subset=['simple_return', 'log_return'], inplace=True)

        cdf_values = calculate_cdf_values(asset_df)
        
        mc_results = mc_bootstrap(cdf_values['S0'], cdf_values['interpolated_cdf_values'], cdf_values['sorted_values'], time_steps=time_steps, iterations=iterations)
        
        results[ticker] = {
            'returns': asset_df[['simple_return', 'log_return']].to_dict(orient='list'),
            'cdf_values': cdf_values,
            'monte_carlo': mc_results
        }

    return results

def calculate_cdf_values(asset_df):
    sorted_values = np.unique(np.sort(asset_df['log_return']))
    ecdf = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
    cs = CubicSpline(sorted_values, ecdf)
    interpolated_cdf_values = cs(sorted_values)

    min_length = min(len(sorted_values), len(interpolated_cdf_values))
    sorted_values = sorted_values[:min_length]
    interpolated_cdf_values = interpolated_cdf_values[:min_length]
    sf_interpolated = 1 - interpolated_cdf_values
    S0 = asset_df['price'].iloc[-1]
    mu = np.median(asset_df['log_return'])

    return {
        'S0': float(S0),
        'sf_interpolated': sf_interpolated.tolist(),
        'sorted_values': sorted_values.tolist(),
        'interpolated_cdf_values': interpolated_cdf_values.tolist(),
        'mu': float(mu)
    }

def mc_bootstrap(S0, cdf_empirical_interpolated, sorted_values, time_steps, iterations):
    def _run_simulation(time_steps, iterations):                     
        U = np.random.rand(time_steps, iterations)
        Z = np.interp(U, cdf_empirical_interpolated, sorted_values)
        factor = np.exp(Z)
        paths = S0 * np.cumprod(factor, axis=0)
        arrival_values = paths[-1]
        return arrival_values
    
    arrival_values = _run_simulation(time_steps, iterations)
    
    return {
        'mean': float(np.mean(arrival_values)),
        'median': float(np.median(arrival_values)),
        'std': float(np.std(arrival_values)),
        'min': float(np.min(arrival_values)),
        'max': float(np.max(arrival_values)),
        'percentiles': {
            '1%': float(np.percentile(arrival_values, 1)),
            '5%': float(np.percentile(arrival_values, 5)),
            '25%': float(np.percentile(arrival_values, 25)),
            '75%': float(np.percentile(arrival_values, 75)),
            '95%': float(np.percentile(arrival_values, 95)),
            '99%': float(np.percentile(arrival_values, 99))
        },
        'all_arrivals': arrival_values.tolist()  # Convert numpy array to list for JSON serialization
    }
def save_to_json(data, filename):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    export_directory = os.path.join(current_directory, "export")
    os.makedirs(export_directory, exist_ok=True)
    
    file_path = os.path.join(export_directory, filename)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {file_path}")

def run_bootstrap(stocks, period, iterations, time_steps):
    try:
        ddb_data = query_dolphindb()
        if ddb_data is None:
            raise Exception("Failed to query DolphinDB")

        results = calculate_returns(ddb_data, stocks.split(','), period, iterations, time_steps)
        return results

    except Exception as e:
        print(f"Error in bootstrap execution: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise
if __name__ == "__main__":
    # This part is now only for testing purposes
    test_stocks = "PETR4,VALE3"
    test_period = 12
    test_iterations = 1000  # Default number of iterations for Monte Carlo simulation
    test_time_steps = 252   # Default number of time steps (approximately 1 trading year)
    results = run_bootstrap(test_stocks, test_period, test_iterations, test_time_steps)
    print(json.dumps(results, indent=2))