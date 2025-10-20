import dolphindb as ddb

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Create the database and table
s.run("""
// Create the database if it doesn't exist
if (!existsDatabase('dfs://yfs')) {
    db = database('dfs://yfs', RANGE, month(1994.01M)..month(2027.12M))
}

// Load the existing database
else {
    db = database('dfs://yfs')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_1m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_1m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_5m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_5m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_15m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_15m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_60m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_60m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_90m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_90m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_1d')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_1d', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'stockdata_1wk')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'stockdata_1wk', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_1m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_1m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_5m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_5m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_15m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_15m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_60m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_60m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_90m')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_90m', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_1d')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_1d', 'Datetime')
}

// Create the stockdata table if it doesn't exist
if (!existsTable('dfs://yfs', 'currency_1wk')) {
    stockSchema = table(1000:0, `Datetime`Symbol`Open`High`Low`Close`AdjClose`Volume`Dividends`Stock_Splits, 
                        [DATETIME, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG, DOUBLE, DOUBLE])
    db.createPartitionedTable(stockSchema, 'currency_1wk', 'Datetime')
}
""")

print("Database 'yfs' and table 'stockdata' created successfully with monthly RANGE partitions!")