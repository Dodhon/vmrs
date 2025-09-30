import pandas as pd
import os

# Define paths
input_csv = "vendor data/Master Parts list for Richard 06.25.25 (1).csv"
output_dir = "vendor data"

# Read CSV
df = pd.read_csv(input_csv)

print(f"Loaded {len(df)} rows from {input_csv}")
print(f"Columns: {', '.join(df.columns)}\n")

# Create sorted CSV for each column
for column in df.columns:
    # Sort by current column
    sorted_df = df.sort_values(by=column)
    
    # Create filename
    safe_column_name = column.replace(' ', '_').replace('/', '_')
    output_file = os.path.join(output_dir, f"Master_Parts_sorted_by_{safe_column_name}.csv")
    
    # Save sorted CSV
    sorted_df.to_csv(output_file, index=False)
    print(f"Created: {output_file}")

print(f"\nGenerated {len(df.columns)} sorted CSV files in {output_dir}/")
