import dolphindb as ddb

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Define a script to find and remove duplicates in the options table
script = """
def removeDuplicatesOptions() {
    optionsData = loadTable("dfs://oplab", "new_options")
    
    // Find duplicates based on symbol, time, and type
    duplicates = select symbol, time, type, count(*) as cnt from optionsData 
                 group by symbol, time, type having count(*) > 1
    
    if (size(duplicates) > 0) {
        // Select unique records without applying first() to grouped columns
        uniqueOptionsData = select symbol, time, type, 
                                   first(spot_price) as spot_price, first(spot_symbol) as spot_symbol, 
                                   first(due_date) as due_date, first(strike) as strike, 
                                   first(premium) as premium, first(maturity_type) as maturity_type, 
                                   first(days_to_maturity) as days_to_maturity, first(moneyness) as moneyness, 
                                   first(delta) as delta, first(gamma) as gamma, first(vega) as vega, 
                                   first(theta) as theta, first(rho) as rho, first(volatility) as volatility, 
                                   first(poe) as poe, first(bs) as bs
                            from optionsData
                            group by symbol, time, type
        
        // Create a new partitioned table with unique data
        db = database("dfs://oplab")
        db.dropTable("new_options")  // Drop the old table
        newOptionsTable = db.createPartitionedTable(uniqueOptionsData, "new_options", "time")
        newOptionsTable.append!(uniqueOptionsData)
    }
    
    return size(duplicates)
}

removeDuplicatesOptions()
"""

# Run the script to remove duplicates
num_duplicates_removed = s.run(script)

# Print the result
if num_duplicates_removed == 0:
    print("No duplicates found in the options table.")
else:
    print(f"Removed {num_duplicates_removed} duplicate entries from the options table.")