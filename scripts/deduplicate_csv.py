#!/usr/bin/env python3
"""
Deduplicate VMRS CSV by combining descriptions for the same code.

Groups rows by code_9d (or code_6d for assemblies) and combines descriptions.
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set


def combine_descriptions(descriptions: List[str]) -> str:
    """
    Combine multiple descriptions into one, removing duplicates and OCR artifacts.
    
    Args:
        descriptions: List of description strings
        
    Returns:
        Combined description string
    """
    # Filter out empty descriptions
    descriptions = [d.strip() for d in descriptions if d.strip()]
    
    if not descriptions:
        return ""
    
    # Remove exact duplicates
    unique_descriptions = []
    seen = set()
    for desc in descriptions:
        desc_lower = desc.lower()
        if desc_lower not in seen:
            seen.add(desc_lower)
            unique_descriptions.append(desc)
    
    # If only one unique description, return it
    if len(unique_descriptions) == 1:
        return unique_descriptions[0]
    
    # If descriptions are very similar (one is substring of another), keep the longer one
    filtered = []
    for desc in unique_descriptions:
        is_substring = False
        desc_lower = desc.lower()
        for other_desc in unique_descriptions:
            if desc != other_desc and desc_lower in other_desc.lower():
                is_substring = True
                break
        if not is_substring:
            filtered.append(desc)
    
    # If filtering removed everything, use original unique list
    if not filtered:
        filtered = unique_descriptions
    
    # Combine with semicolon separator
    combined = " / ".join(filtered)
    
    return combined


def deduplicate_csv(input_file: str, output_file: str = None):
    """
    Deduplicate CSV by code, combining descriptions.
    
    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV (default: input_file with _deduplicated suffix)
    """
    print("🔄 VMRS CSV Deduplication")
    print("=" * 70)
    
    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_deduplicated{input_path.suffix}")
    
    print(f"📖 Input:  {input_file}")
    print(f"💾 Output: {output_file}")
    
    # Read CSV
    print(f"\n📊 Reading CSV...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    print(f"✅ Read {len(rows):,} rows")
    
    # Group by code
    code_to_rows = defaultdict(list)
    
    for row in rows:
        code_9d = row.get('code_9d', '').strip()
        code_6d = row.get('code_6d', '').strip()
        
        # Use code_9d if available, otherwise code_6d
        code = code_9d if code_9d else code_6d
        
        if code:
            code_to_rows[code].append(row)
    
    print(f"📊 Found {len(code_to_rows):,} unique codes")
    
    # Count duplicates
    duplicates = {code: rows_list for code, rows_list in code_to_rows.items() if len(rows_list) > 1}
    print(f"⚠️  {len(duplicates):,} codes have duplicates")
    
    # Create deduplicated rows
    deduplicated_rows = []
    stats = {
        'total_original': len(rows),
        'total_deduplicated': 0,
        'codes_with_duplicates': len(duplicates),
        'descriptions_combined': 0
    }
    
    print(f"\n🔄 Deduplicating...")
    
    for code, rows_list in code_to_rows.items():
        if len(rows_list) == 1:
            # No duplicates, keep as-is
            deduplicated_rows.append(rows_list[0])
        else:
            # Has duplicates, combine
            # Take the first row as base
            base_row = rows_list[0].copy()
            
            # Collect all descriptions
            descriptions = [r.get('description', '').strip() for r in rows_list if r.get('description', '').strip()]
            
            # Combine descriptions
            combined_desc = combine_descriptions(descriptions)
            base_row['description'] = combined_desc
            
            # For other fields, prefer non-empty values
            for field in fieldnames:
                if field not in ['code_9d', 'code_6d', 'description']:
                    # Try to find a non-empty value
                    for r in rows_list:
                        if r.get(field, '').strip():
                            base_row[field] = r[field]
                            break
            
            deduplicated_rows.append(base_row)
            stats['descriptions_combined'] += len(descriptions) - 1
    
    stats['total_deduplicated'] = len(deduplicated_rows)
    
    # Write deduplicated CSV
    print(f"\n💾 Writing deduplicated CSV...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduplicated_rows)
    
    print(f"✅ Wrote {len(deduplicated_rows):,} rows")
    
    # Print statistics
    print(f"\n" + "=" * 70)
    print("📊 DEDUPLICATION STATISTICS")
    print("=" * 70)
    print(f"Original rows:        {stats['total_original']:,}")
    print(f"Deduplicated rows:    {stats['total_deduplicated']:,}")
    print(f"Rows removed:         {stats['total_original'] - stats['total_deduplicated']:,}")
    print(f"Codes with duplicates: {stats['codes_with_duplicates']:,}")
    print(f"Descriptions combined: {stats['descriptions_combined']:,}")
    print(f"\n✅ Deduplication complete!")
    print(f"📁 Output saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deduplicate VMRS CSV by combining descriptions')
    parser.add_argument('--input', default='csv data/VMRS_COMPLETE_v20_MASTER.csv',
                       help='Path to input CSV file')
    parser.add_argument('--output', default=None,
                       help='Path to output CSV file (default: input_file with _deduplicated suffix)')
    
    args = parser.parse_args()
    
    deduplicate_csv(args.input, args.output)


if __name__ == "__main__":
    main()

