import dolphindb as ddb

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Script to delete the table
delete_table_script = """
if (existsTable('dfs://zommalab', 'vanilla')) {
    db = database('dfs://zommalab')
    dropTable(db, 'vanilla')
    print("Table 'vanilla' in 'dfs://zommalab' has been successfully deleted.")
} else {
    print("Table 'vanilla' in 'dfs://zommalab' does not exist.")
}
"""

# Run the delete table script
result = s.run(delete_table_script)

# Print the result
print(result)

# Close the connection
s.close()
