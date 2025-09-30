#!/usr/bin/env python3
import csv
import json
import os
import sys

ROOT = "/Users/thuptenwangpo/Documents/GitHub/vrms"
IN_DIR = os.path.join(ROOT, "csv data")
OUT_FILE = os.path.join(IN_DIR, "VMRS_COMPLETE_v20_MASTER.csv")
SUMMARY_FILE = os.path.join(IN_DIR, "master_summary.json")

def main():
	# Find all CSV files (exclude validation and master files)
	csv_files = [
		os.path.join(IN_DIR, f) for f in os.listdir(IN_DIR)
		if f.endswith('.csv') and 'validation' not in f.lower() and 'master' not in f.lower()
	]
	csv_files.sort()
	
	if not csv_files:
		print("No CSV files found to combine.", file=sys.stderr)
		sys.exit(1)
	
	print(f"Found {len(csv_files)} CSV files to combine")
	
	# Statistics
	stats = {
		"files_processed": 0,
		"total_rows": 0,
		"rows_9d": 0,
		"rows_6d": 0,
	}
	
	# Combine all CSVs
	with open(OUT_FILE, 'w', newline='', encoding='utf-8') as out_f:
		writer = None
		
		for csv_path in csv_files:
			filename = os.path.basename(csv_path)
			
			with open(csv_path, 'r', encoding='utf-8') as in_f:
				reader = csv.DictReader(in_f)
				
				# Write header on first file only
				if writer is None:
					fieldnames = reader.fieldnames
					writer = csv.DictWriter(out_f, fieldnames=fieldnames)
					writer.writeheader()
				
				# Write all rows from this file
				rows_in_file = 0
				for row in reader:
					writer.writerow(row)
					stats["total_rows"] += 1
					rows_in_file += 1
					
					# Count by type
					if row.get('code_9d'):
						stats["rows_9d"] += 1
					if row.get('code_6d'):
						stats["rows_6d"] += 1
			
			stats["files_processed"] += 1
			print(f"  [{stats['files_processed']}/{len(csv_files)}] {filename}: {rows_in_file} rows")
	
	# Write summary
	with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
		json.dump(stats, f, indent=2)
	
	# Print summary
	print(f"\n✅ Master CSV created: {OUT_FILE}")
	print(f"   Total rows: {stats['total_rows']:,}")
	print(f"   9-digit codes: {stats['rows_9d']:,}")
	print(f"   6-digit codes: {stats['rows_6d']:,}")
	print(f"   Files combined: {stats['files_processed']}")

if __name__ == "__main__":
	main()

