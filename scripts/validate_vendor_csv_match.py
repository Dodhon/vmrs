#!/usr/bin/env python3
"""
Validate that two vendor CSV files are identical.

Compares:
- Motors Part Cleanup - Return Data (2).csv (project root)
- vendor data/checked/Motors Part Cleanup - Return Data.csv
"""

import pandas as pd
import sys

FILE_A = "Motors Part Cleanup - Return Data (2).csv"
FILE_B = "vendor data/checked/Motors Part Cleanup - Return Data.csv"


def main():
    print(f"Comparing:\n  A: {FILE_A}\n  B: {FILE_B}\n")
    
    df_a = pd.read_csv(FILE_A)
    df_b = pd.read_csv(FILE_B)
    
    # Basic checks
    print(f"Rows:    A={len(df_a)}, B={len(df_b)}, Match={len(df_a) == len(df_b)}")
    print(f"Columns: A={len(df_a.columns)}, B={len(df_b.columns)}, Match={list(df_a.columns) == list(df_b.columns)}")
    
    if list(df_a.columns) != list(df_b.columns):
        print(f"\n⚠️  Column mismatch:")
        print(f"  Only in A: {set(df_a.columns) - set(df_b.columns)}")
        print(f"  Only in B: {set(df_b.columns) - set(df_a.columns)}")
        print(f"\n  Comparing common columns only...")
        common_cols = [c for c in df_a.columns if c in df_b.columns]
        df_a = df_a[common_cols]
        df_b = df_b[common_cols]
    
    if len(df_a) != len(df_b):
        print(f"\n❌ Row count mismatch: {len(df_a)} vs {len(df_b)}")
        sys.exit(1)
    
    # Compare content
    diff = (df_a != df_b) & ~(df_a.isna() & df_b.isna())
    diff_count = diff.sum().sum()
    
    if diff_count == 0:
        print(f"\n✅ Files are identical!")
    else:
        print(f"\n❌ Files differ in {diff_count} cells")
        # Show first few differences
        for col in df_a.columns:
            col_diff = diff[col]
            if col_diff.any():
                diff_rows = col_diff[col_diff].index[:3]
                for row in diff_rows:
                    print(f"  Row {row}, {col}: '{df_a.loc[row, col]}' vs '{df_b.loc[row, col]}'")
        sys.exit(1)


if __name__ == "__main__":
    main()

