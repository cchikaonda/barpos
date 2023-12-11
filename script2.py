import pandas as pd

# Reading the deduplicated CSV file
input_data = "/var/www/ghii/client_purchases_deduplicated.csv"
df = pd.read_csv(input_data)


# Replacing PII with generic placeholders
df['First Name'] = 'FirstName'
df['Last Name'] = 'LastName'
df['Email'] = 'email@example.com'
df['Phone'] = '000-000-0000'
df['Address'] = 'Anonymized Address'

# Exporting the anonymized dataset to a CSV file
output_data = "clients_deidentified.csv"
df.to_csv(output_data, index=False)
