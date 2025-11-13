#!/usr/bin/env python3
"""
Extract VMRS hierarchy (System-Assembly-Component) from deduplicated CSV to a new CSV.

This script:
1. Reads VMRS_COMPLETE_v20_MASTER_deduplicated.csv
2. Extracts system, assembly, and component from code_9d
3. Outputs hierarchy mapping to a CSV file
"""

import csv
import re
import sys
from typing import Set, Dict
from pathlib import Path
from collections import defaultdict


def parse_code_9d(code_9d: str) -> tuple:
    """
    Parse code_9d to extract system, assembly, and component codes.
    
    Args:
        code_9d: Format "174-001-110" (system-assembly-component)
        
    Returns:
        Tuple of (system_code, assembly_code, component_code) or (None, None, None) if invalid
    """
    if not code_9d or not code_9d.strip():
        return (None, None, None)
    
    code_9d = code_9d.strip()
    
    # Validate format: XXX-XXX-XXX
    if not re.match(r'^\d{3}-\d{3}-\d{3}$', code_9d):
        return (None, None, None)
    
    parts = code_9d.split('-')
    system_code = parts[0]
    assembly_code = f"{parts[0]}-{parts[1]}"
    component_code = code_9d
    
    return (system_code, assembly_code, component_code)


def extract_hierarchy_to_csv(input_csv: str, output_csv: str):
    """
    Extract VMRS hierarchy from CSV and write to a new CSV.
    
    Args:
        input_csv: Path to VMRS_COMPLETE_v20_MASTER_deduplicated.csv
        output_csv: Path to output CSV file
    """
    print("🚀 VMRS Hierarchy Extraction to CSV")
    print("=" * 70)
    
    # Read input CSV
    print(f"\n📊 Reading CSV: {input_csv}")
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"✅ Read {len(rows):,} rows")
    
    # Track unique systems, assemblies, and components
    systems: Dict[str, str] = {}  # code -> name
    assemblies: Dict[str, Dict[str, str]] = {}  # code -> {system_code, name}
    components: Dict[str, Dict[str, str]] = {}  # code -> {assembly_code, name, description}
    
    # Statistics
    stats = {
        'systems': 0,
        'assemblies': 0,
        'components': 0,
        'skipped': 0
    }
    
    print(f"\n🔄 Processing rows...")
    
    # Process each row
    for i, row in enumerate(rows):
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1:,}/{len(rows):,} rows...")
        
        code_9d = row.get('code_9d', '').strip()
        description = row.get('description', '').strip()
        
        if not code_9d:
            stats['skipped'] += 1
            continue
        
        # Parse code_9d to get system, assembly, component
        system_code, assembly_code, component_code = parse_code_9d(code_9d)
        
        if not system_code:
            stats['skipped'] += 1
            continue
        
        # Track system
        if system_code not in systems:
            systems[system_code] = f"System {system_code}"
            stats['systems'] += 1
        
        # Track assembly
        if assembly_code not in assemblies:
            assemblies[assembly_code] = {
                'system_code': system_code,
                'name': f"Assembly {assembly_code}"
            }
            stats['assemblies'] += 1
        
        # Track component
        if component_code not in components:
            components[component_code] = {
                'assembly_code': assembly_code,
                'name': description or f"Component {component_code}",
                'description': description
            }
            stats['components'] += 1
    
    # Write output CSV
    print(f"\n📝 Writing hierarchy to CSV: {output_csv}")
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'system_code',
            'system_name',
            'assembly_code',
            'assembly_name',
            'component_code',
            'component_name',
            'component_description'
        ])
        
        # Write component rows (each component shows its full hierarchy)
        for component_code, comp_data in sorted(components.items()):
            assembly_code = comp_data['assembly_code']
            assembly_data = assemblies[assembly_code]
            system_code = assembly_data['system_code']
            
            writer.writerow([
                system_code,
                systems[system_code],
                assembly_code,
                assembly_data['name'],
                component_code,
                comp_data['name'],
                comp_data['description']
            ])
    
    print(f"✅ Wrote {stats['components']:,} component rows")
    
    # Print statistics
    print(f"\n" + "=" * 70)
    print("📊 EXTRACTION STATISTICS")
    print("=" * 70)
    print(f"Unique Systems: {stats['systems']}")
    print(f"Unique Assemblies: {stats['assemblies']}")
    print(f"Unique Components: {stats['components']:,}")
    print(f"Skipped rows: {stats['skipped']}")
    print(f"\n✅ Output written to: {output_csv}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract VMRS hierarchy from deduplicated CSV to a new CSV')
    parser.add_argument('--input', 
                       default='csv data/VMRS_COMPLETE_v20_MASTER_deduplicated.csv',
                       help='Path to deduplicated VMRS CSV file')
    parser.add_argument('--output',
                       default='csv data/VMRS_hierarchy_mapping.csv',
                       help='Path to output CSV file')
    
    args = parser.parse_args()
    
    # Run extraction
    extract_hierarchy_to_csv(
        input_csv=args.input,
        output_csv=args.output
    )


if __name__ == "__main__":
    main()

