#!/usr/bin/env python3

import sys
import os
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)
from backend.apps.utils.dict import TICKERS_DICT

from datetime import datetime, timedelta
import requests
import csv
import dolphindb as ddb
import pandas as pd
import time

# Connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Create the database and table if they don't exist
s.run("""
if (!existsDatabase('dfs://oplab')) {
    db = database('dfs://oplab', RANGE, 2012.01M..2027.12M)
}

if (!existsTable('dfs://oplab', 'stockinfo')) {
    schema = table(
        1:0,
        `symbol`type`name`open`high`low`close`volume`financial_volume`trades`bid`ask`category`contract_size`created_at`updated_at`variation`ewma_1y_max`ewma_1y_min`ewma_1y_percentile`ewma_1y_rank`ewma_6m_max`ewma_6m_min`ewma_6m_percentile`ewma_6m_rank`ewma_current`has_options`iv_1y_max`iv_1y_min`iv_1y_percentile`iv_1y_rank`iv_6m_max`iv_6m_min`iv_6m_percentile`iv_6m_rank`iv_current`middle_term_trend`semi_return_1y`short_term_trend`stdv_1y`stdv_5d`beta_ibov`garch11_1y`isin`correl_ibov`entropy`security_category`sector`quotation_form`market_maker`highest_options_volume_rank`long_name`bid_volume`ask_volume`time`previous_close,
        [STRING, STRING, STRING, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, LONG, INT, DOUBLE, DOUBLE, STRING, INT, TIMESTAMP, TIMESTAMP, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, BOOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, INT, DOUBLE, INT, DOUBLE, DOUBLE, DOUBLE, DOUBLE, STRING, DOUBLE, DOUBLE, INT, STRING, INT, BOOL, INT, STRING, LONG, LONG, TIMESTAMP, DOUBLE]
    )
    db = database('dfs://oplab')
    db.createPartitionedTable(schema, 'stockinfo', 'time')
}
""")
print("Database and table created successfully with monthly partitions!")

# Verify if the table was created
table_exists = s.run("existsTable('dfs://oplab', 'stockinfo')")
print(f"Table 'stockinfo' exists in 'dfs://oplab': {table_exists}")

# Optionally print the table schema for confirmation
try:
    schema_info = s.run("""
        def getSchema() {
            t = loadTable('dfs://oplab', 'stockinfo')
            return schema(t)
        }
        getSchema()
    """)
    print("Table schema:")
    print(schema_info)
except Exception as e:
    print(f"Error getting table schema: {str(e)}")

# ----------------------------
# Check if every symbol in TICKERS_DICT["TODOS"] is present in the stockinfo table.
# ----------------------------

missing_symbols = []
for symbol in TICKERS_DICT["IBOV"]:
    # Build the query to count occurrences of the symbol in the table.
    query = "select count(*) as cnt from loadTable('dfs://oplab', 'stockinfo') where symbol='{}'".format(symbol)
    result = s.run(query)
    # Assuming result is a Pandas DataFrame, get the count from the "cnt" column.
    count = result['cnt'].iloc[0]
    if count == 0:
        missing_symbols.append(symbol)

if missing_symbols:
    print("The following symbols are missing in the stockinfo table:")
    for sym in missing_symbols:
        print(" -", sym)
else:
    print("All symbols from TICKERS_DICT['IBOV'] are present in the stockinfo table.")