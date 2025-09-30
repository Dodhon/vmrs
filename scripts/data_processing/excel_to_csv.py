import pandas as pd
import os

# Define paths
excel_file = "vendor data/Master Parts list for Richard 06.25.25 (1).xlsx"
csv_file = "vendor data/Master Parts list for Richard 06.25.25 (1).csv"

# Read Excel file
df = pd.read_excel(excel_file)

# Save as CSV
df.to_csv(csv_file, index=False)

print(f"Converted {excel_file} to {csv_file}")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
