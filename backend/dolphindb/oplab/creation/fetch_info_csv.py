import requests
import csv
import datetime

# Define API key and headers
headers = {
    'Access-Token': 'NV0MENA0YZ9bgJA/Wf+F+tROe+eYX9SpUBuhmxNNkeIVuQKf+/wtVkYT4gGo0uvg--tTAJG2No3ZgblMOUkEql4g==--NzllMzczOTg2ZWI5ZmJlN2U2MjBmMDA3NGIxODcxOWQ='
}

# Define base URL
base_url = 'https://api.oplab.com.br/v3/market/stocks/all'
limit = 30  # Total number of pages to fetch

# Define query parameters
params = {
    'page': 1,
    'per': 20,  # Fetch up to 2 stocks per page as needed
    'rank_by': 'financial_volume',
    'sort': 'desc',
    'financial_volume_start': 10000
}

filtered_stocks = []

# Function to convert millisecond timestamp to formatted date-time string
def convert_timestamp(ms_timestamp):
    if ms_timestamp is None:
        return None
    timestamp = ms_timestamp / 1000  # convert milliseconds to seconds
    date_time = datetime.datetime.fromtimestamp(timestamp)
    return date_time.strftime('%Y-%m-%d %H:%M:%S')

# Loop until the page limit is reached
while params['page'] <= limit:
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code != 200:
        print("Failed to retrieve data", response.status_code, response.text)
        break

    stocks_data = response.json()
    
    # Check if the response has any stock data
    if not isinstance(stocks_data, list) or len(stocks_data) == 0:
        break

    print(f"Page {params['page']}: Retrieved {len(stocks_data)} stocks.")
    
    for stock in stocks_data:
        # Decode the sector value from Unicode escape sequences to UTF-8
        sector = stock.get('sector', '')
        human_readable_sector = sector  # Remove encoding/decoding

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
            'entropy': stock.get('entropy'),
            'security_category': stock.get('security_category'),
            'sector': human_readable_sector,
            'quotation_form': stock.get('quotation_form'),
            'market_maker': stock.get('market_maker'),
            'highest_options_volume_rank': stock.get('highest_options_volume_rank'),
            'long_name': stock.get('long_name'),
            'bid_volume': stock.get('bid_volume'),
            'ask_volume': stock.get('ask_volume'),
            'time': convert_timestamp(stock.get('time')),
            'previous_close': stock.get('previous_close')
        }
        filtered_stocks.append(filtered_stock)
    
    # Move to the next page
    params['page'] += 1

print(f"Total stocks retrieved: {len(filtered_stocks)}")

if filtered_stocks:
    print("Selected stock:")
    for key, value in filtered_stocks[-1].items():
        print(f"{key}: {value}")
else:
    print("No stocks were found.")

# Save the filtered stocks to a CSV file
csv_filename = "all_b3_stocks.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    if filtered_stocks:
        fieldnames = filtered_stocks[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for stock in filtered_stocks:
            writer.writerow(stock)

print(f"Data has been written to {csv_filename}")