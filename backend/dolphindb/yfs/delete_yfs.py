import dolphindb as ddb

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")

# Script to delete the database
delete_script = """
if (existsDatabase('dfs://yfs')) {
    dropDatabase('dfs://yfs')
    print("Database 'dfs://yfs' has been successfully deleted.")
} else {
    print("Database 'dfs://yfs' does not exist.")
}
"""

# Run the delete script
result = s.run(delete_script)

# Print the result
print(result)

# Close the connection
s.close()