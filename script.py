import pandas as pd

# Reading the CSV file
input_data = "/var/www/ghii/client_purchases.csv"
df = pd.read_csv(input_data)

# Finding and identify duplicate records
duplicate_records = df[df.duplicated(keep="first")]

# Removing duplicate records
df = df.drop_duplicates(keep="first")

# Exporting the cleaned CSV file
output_data_deduplicated = "client_purchases_deduplicated.csv"
df.to_csv(output_data_deduplicated, index=False)

# Identifying unique clients and assigning