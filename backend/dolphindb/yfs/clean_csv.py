import os
import glob

# Get the current directory
current_directory = os.getcwd()

# Find all .csv files in the current directory
csv_files = glob.glob(os.path.join(current_directory, "*.csv"))

# Delete each .csv file
for file in csv_files:
    try:
        os.remove(file)
        #print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")

print("All .csv files deleted.")
