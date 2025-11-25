#!/usr/bin/env python3
"""
Enrich VMRS codes with aggregated vendor part data.

This script:
1. Loads VMRS official code descriptions
2. Loads vendor part data
3. Aggregates vendor data by VMRS code (concatenates with " / ")
4. Joins with VMRS codes to create enriched dataset
5. Exports Neo4j-ready CSV

Output: One row per VMRS code with aggregated vendor information.
"""

import pandas as pd
import sys
from pathlib import Path

def main():
    """Main execution function."""
    print("🚀 VMRS Code Enrichment with Vendor Data")
    print("=" * 70)
    
    # File paths
    vmrs_file = 'knowledge_graph_output/combined_triple_extraction_and_md_tables_codes.csv'
    vendor_file = 'vendor data/checked/Motors Part Cleanup - Return Data.csv'
    output_file = 'knowledge_graph_output/vmrs_codes_enriched_with_vendor_data.csv'
    
    # Step 1: Load VMRS codes
    print(f"\n📊 Loading VMRS codes from: {vmrs_file}")
    vmrs_df = pd.read_csv(vmrs_file, encoding='utf-8')
    print(f"✅ Loaded {len(vmrs_df):,} VMRS codes")
    
    # Step 2: Load vendor parts
    print(f"\n📊 Loading vendor parts from: {vendor_file}")
    vendor_df = pd.read_csv(vendor_file, encoding='utf-8')
    print(f"✅ Loaded {len(vendor_df):,} vendor parts")
    
    # Clean VMRS codes
    print(f"\n🧹 Cleaning and normalizing VMRS codes...")
    vendor_df['VMRS'] = vendor_df['VMRS'].astype(str).str.strip()
    vmrs_df['code'] = vmrs_df['code'].astype(str).str.strip()
    
    # Remove invalid VMRS codes
    vendor_df = vendor_df[vendor_df['VMRS'] != '']
    vendor_df = vendor_df[vendor_df['VMRS'] != 'nan']
    print(f"✅ {len(vendor_df):,} vendor parts with valid VMRS codes")
    
    # Step 3: Aggregate vendor data by VMRS code
    print(f"\n🔄 Aggregating vendor data by VMRS code...")
    
    vendor_agg = vendor_df.groupby('VMRS').agg({
        'PART': lambda x: ' / '.join(sorted(set(x.dropna().astype(str).str.strip()))),
        'DESCRIPTION': lambda x: ' / '.join(sorted(set(x.dropna().str.strip()))),
        'MANF_PARTMFR_NAME': lambda x: ' / '.join(sorted(set(x.dropna().str.strip()))),
        'MANF_PARTMFR': lambda x: ' / '.join(sorted(set(x.dropna().str.strip()))),
        'SYSTEM_': 'first',
        'ASSEMBLY_': 'first',
        'COMPONENT_': 'first'
    }).reset_index()
    
    # Add part count
    vendor_agg['part_count'] = vendor_df.groupby('VMRS').size().values
    
    print(f"✅ Aggregated data for {len(vendor_agg):,} unique VMRS codes")
    
    # Step 4: Join with VMRS official descriptions
    print(f"\n🔗 Joining with VMRS official descriptions...")
    
    enriched_df = vmrs_df.merge(
        vendor_agg,
        left_on='code',
        right_on='VMRS',
        how='left'
    )
    
    print(f"✅ Created enriched dataset with {len(enriched_df):,} rows")
    
    # Rename and reorder columns
    print(f"\n🏷️  Renaming columns for Neo4j...")
    
    enriched_df = enriched_df.rename(columns={
        'code': 'vmrs_code',
        'description': 'vmrs_official_description',
        'PART': 'vendor_part_numbers',
        'DESCRIPTION': 'vendor_descriptions',
        'MANF_PARTMFR_NAME': 'manufacturers',
        'MANF_PARTMFR': 'manf_codes',
        'SYSTEM_': 'system_name',
        'ASSEMBLY_': 'assembly_name',
        'COMPONENT_': 'component_name'
    })
    
    # Select and reorder columns
    output_columns = [
        'vmrs_code',
        'vmrs_official_description',
        'vendor_part_numbers',
        'vendor_descriptions',
        'manufacturers',
        'manf_codes',
        'part_count',
        'system_name',
        'assembly_name',
        'component_name'
    ]
    
    enriched_df = enriched_df[output_columns]
    
    # Fill NaN with empty strings
    enriched_df = enriched_df.fillna('')
    
    # Step 5: Export results
    print(f"\n💾 Exporting to: {output_file}")
    enriched_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ Export complete!")
    
    # Print statistics
    print(f"\n" + "=" * 70)
    print("📊 ENRICHMENT STATISTICS")
    print("=" * 70)
    print(f"Total VMRS codes: {len(enriched_df):,}")
    print(f"VMRS codes with vendor parts: {len(enriched_df[enriched_df['vendor_part_numbers'] != '']):,}")
    print(f"VMRS codes without vendor parts: {len(enriched_df[enriched_df['vendor_part_numbers'] == '']):,}")
    print(f"Total vendor parts mapped: {vendor_df['VMRS'].notna().sum():,}")
    print(f"Unique VMRS codes in vendor data: {len(vendor_agg):,}")
    
    # Sample output
    print(f"\n" + "=" * 70)
    print("📋 SAMPLE OUTPUT (First enriched code with vendor data)")
    print("=" * 70)
    
    sample = enriched_df[enriched_df['vendor_part_numbers'] != ''].head(1)
    if not sample.empty:
        for col in output_columns:
            value = sample.iloc[0][col]
            if len(str(value)) > 100:
                value = str(value)[:97] + "..."
            print(f"{col}: {value}")
    
    print(f"\n✅ Enrichment complete!")


if __name__ == "__main__":
    main()

