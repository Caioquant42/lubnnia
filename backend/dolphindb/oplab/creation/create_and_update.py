import dolphindb as ddb
import csv
from datetime import datetime
import pandas as pd

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

# Get table schema
try:
    schema = s.run("""
        def getSchema() {
            t = loadTable('dfs://oplab', 'stockinfo')
            return schema(t)
        }
        getSchema()
    """)
    print("Table schema:")
    print(schema)
except Exception as e:
    print(f"Error getting table schema: {str(e)}")

# Function to convert date string to the proper timestamp format
def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

# Read data from the CSV file into a DataFrame
csv_filename = "all_b3_stocks.csv"
data = pd.read_csv(csv_filename)

# Convert timestamp fields
data['created_at'] = pd.to_datetime(data['created_at'].apply(parse_date))
data['updated_at'] = pd.to_datetime(data['updated_at'].apply(parse_date))
data['time'] = pd.to_datetime(data['time'])

# Convert and prepare each column according to the schema:

# String columns
data['symbol'] = data['symbol'].astype(str)
data['type']   = data['type'].astype(str)
data['name']   = data['name'].astype(str)
data['category'] = data['category'].astype(str)
data['isin']   = data['isin'].astype(str)
data['long_name'] = data['long_name'].astype(str)
data['sector']    = data['sector'].astype(str)

# Double columns (float)
double_cols = ['open', 'high', 'low', 'close', 'bid', 'ask', 'variation',
               'ewma_1y_max', 'ewma_1y_min', 'ewma_1y_percentile', 'ewma_1y_rank',
               'ewma_6m_max', 'ewma_6m_min', 'ewma_6m_percentile', 'ewma_6m_rank',
               'ewma_current', 'iv_1y_max', 'iv_1y_min', 'iv_1y_percentile', 'iv_1y_rank',
               'iv_6m_max', 'iv_6m_min', 'iv_6m_percentile', 'iv_6m_rank', 'iv_current',
               'semi_return_1y', 'stdv_1y', 'stdv_5d', 'beta_ibov', 'garch11_1y',
               'correl_ibov', 'entropy', 'previous_close']
for col in double_cols:
    data[col] = data[col].fillna(0).astype(float)

# LONG columns (integers, 64-bit)
long_cols = ['volume', 'financial_volume', 'bid_volume', 'ask_volume']
for col in long_cols:
    if col in data.columns:
        data[col] = data[col].fillna(0).astype('int64')

# INT columns (32/64-bit integers)
int_cols = ['trades', 'contract_size', 'middle_term_trend', 'short_term_trend',
            'security_category', 'quotation_form', 'highest_options_volume_rank']
for col in int_cols:
    if col in data.columns:
        data[col] = data[col].fillna(0).astype('int64')

# BOOL columns
bool_cols = ['has_options', 'market_maker']
for col in bool_cols:
    if col in data.columns:
        data[col] = data[col].fillna(False).astype(bool)

# Upload the converted DataFrame to the DolphinDB server under the variable name "dfData"
s.upload({"dfData": data})

# Append the uploaded DataFrame to the "stockinfo" table in DolphinDB
s.run("loadTable('dfs://oplab','stockinfo').append!(dfData)")

print("Data inserted into the 'stockinfo' table successfully!")