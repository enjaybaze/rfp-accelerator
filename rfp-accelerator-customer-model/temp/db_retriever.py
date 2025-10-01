import sys
import sqlite3
import pandas as pd
# Path to your SQLite database file
db_path = 'temp/rfp-response.db'
# Connect to the database
conn = sqlite3.connect(db_path)
# Name of the table you want to read
table_name = 'rfp_responses'
# Read the table into a Pandas DataFrame
run_id = sys.argv[1]
df = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE run_id='{run_id}'", conn)
df.to_excel(f'temp/{run_id}.xlsx', index=False)
# Close the database connection
conn.close()
print(df)