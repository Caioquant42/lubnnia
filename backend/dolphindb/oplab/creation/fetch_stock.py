#!/usr/bin/env python3

import sys
import os
import json
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)
from backend.apps.utils.dict import TICKERS_DICT

import requests
import csv
import datetime
from datetime import datetime
import time

# Define API key and headers
headers = {
    'Access-Token': 'NV0MENA0YZ9bgJA/Wf+F+tROe+eYX9SpUBuhmxNNkeIVuQKf+/wtVkYT4gGo0uvg--tTAJG2No3ZgblMOUkEql4g==--NzllMzczOTg2ZWI5ZmJlN2U2MjBmMDA3NGIxODcxOWQ='
}

# Define base URL for "Consultar uma ação" endpoint
base_url = 'https://api.oplab.com.br/v3/market/stocks/{symbol}'

filtered_stocks = []

# Function to convert a millisecond timestamp to formatted date-time string
def convert_timestamp(ms_timestamp):
    if ms_timestamp is None:
        return None
    timestamp = ms_timestamp / 1000  # convert milliseconds to seconds
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Iterate over each symbol in TICKERS_DICT under "IBOV" to perform the query
for symbol in TICKERS_DICT["IBOV"]:
    # Construct the URL with the symbol in the path
    url = base_url.format(symbol=symbol)
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for symbol {symbol}: {response.status_code} {response.text}")
        continue
    print(f"Fetching {symbol} stock data")    

    # The API returns a single JSON object with the stock's details.
    stock = response.json()

    # Build the filtered_stock dictionary using the response schema from the docs.
    filtered_stock = {
        'symbol': stock.get('symbol'),
        'type': stock.get('type'),
        'name': stock.get('name'),
        'open': stock.get('open'),
        'high': stock.get('high'),
        'low': stock.get('low'),
        'close': stock.get('close'),
        'volume': stock.get('volume'),
        'financial_volume': stock.get('financial_volume'),
        'trades': stock.get('trades'),
        'bid': stock.get('bid'),
        'ask': stock.get('ask'),
        'category': stock.get('category'),
        'contract_size': stock.get('contract_size'),
        'created_at': stock.get('created_at'),
        'updated_at': stock.get('updated_at'),
        'variation': stock.get('variation'),
        'ewma_1y_max': stock.get('ewma_1y_max'),
        'ewma_1y_min': stock.get('ewma_1y_min'),
        'ewma_1y_percentile': stock.get('ewma_1y_percentile'),
        'ewma_1y_rank': stock.get('ewma_1y_rank'),
        'ewma_6m_max': stock.get('ewma_6m_max'),
        'ewma_6m_min': stock.get('ewma_6m_min'),
        'ewma_6m_percentile': stock.get('ewma_6m_percentile'),
        'ewma_6m_rank': stock.get('ewma_6m_rank'),
        'ewma_current': stock.get('ewma_current'),
        'has_options': stock.get('has_options'),
        'iv_1y_max': stock.get('iv_1y_max'),
        'iv_1y_min': stock.get('iv_1y_min'),
        'iv_1y_percentile': stock.get('iv_1y_percentile'),
        'iv_1y_rank': stock.get('iv_1y_rank'),
        'iv_6m_max': stock.get('iv_6m_max'),
        'iv_6m_min': stock.get('iv_6m_min'),
        'iv_6m_percentile': stock.get('iv_6m_percentile'),
        'iv_6m_rank': stock.get('iv_6m_rank'),
        'iv_current': stock.get('iv_current'),
        'middle_term_trend': stock.get('middle_term_trend'),
        'semi_return_1y': stock.get('semi_return_1y'),
        'short_term_trend': stock.get('short_term_trend'),
        'stdv_1y': stock.get('stdv_1y'),
        'stdv_5d': stock.get('stdv_5d'),
        'beta_ibov': stock.get('beta_ibov'),
        'garch11_1y': stock.get('garch11_1y'),
        'isin': stock.get('isin'),
        'correl_ibov': stock.get('correl_ibov'),
        'entropy': stock.get('entropy')
    }
    # Additional attributes from the with_financials parameter
    filtered_stock.update({
        'sector': stock.get('sector'),
        'cvmCode': stock.get('cvmCode'),
        'currency': stock.get('currency'),
        'currencyScale': stock.get('currencyScale'),
        'marketMaker': stock.get('marketMaker'),
        'previousClose': stock.get('previousClose')
    })
    # Optionally, if the API returns timestamps as ms, uncomment the following line:
    # filtered_stock['time'] = convert_timestamp(stock.get('time'))
    # Otherwise, if the API returns time as a formatted string, assign directly:
    filtered_stock['time'] = convert_timestamp(stock.get('time'))
    
    filtered_stocks.append(filtered_stock)
    # Optionally: time.sleep(0.5)  # Small delay to avoid potential rate limiting

print(f"Total symbols retrieved: {len(filtered_stocks)}") 

if filtered_stocks:
    print("Selected stock details:")
    for key, value in filtered_stocks[-1].items():
        print(f"{key}: {value}")
else:
    print("No stocks were found.")

# Save the filtered stocks to a CSV file
csv_filename = "IBOV_stocks.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    if filtered_stocks:
        fieldnames = filtered_stocks[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for stock in filtered_stocks:
            writer.writerow(stock)
print(f"Data has been written to {csv_filename}")

# Save the filtered stocks to a JSON file
json_filename = "IBOV_stocks.json"
with open(json_filename, 'w', encoding='utf-8') as json_file:
    json.dump(filtered_stocks, json_file, ensure_ascii=False, indent=4)
print(f"Data has been written to {json_filename}")