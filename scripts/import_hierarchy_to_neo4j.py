#!/usr/bin/env python3
"""
Import VMRS hierarchy (System-Assembly-Component) from deduplicated CSV to Neo4j.

This script:
1. Reads VMRS_COMPLETE_v20_MASTER_deduplicated.csv
2. Extracts system, assembly, and component from code_9d
3. Creates nodes and PART_OF relationships in Neo4j
"""

import csv
import re
import sys
import os
from pathlib import Path
from typing import Set
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.neo4j_client import Neo4jClient

# Load environment variables
load_dotenv()


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


def import_hierarchy_to_neo4j(csv_file: str,
                              neo4j_uri: str = None,
                              neo4j_username: str = None,
                              neo4j_password: str = None):
    """
    Import VMRS hierarchy from CSV to Neo4j.
    
    Args:
        csv_file: Path to VMRS_COMPLETE_v20_MASTER_deduplicated.csv
        neo4j_uri: Neo4j connection URI
        neo4j_username: Neo4j username
        neo4j_password: Neo4j password
    """
    print("🚀 VMRS Hierarchy Import to Neo4j")
    print("=" * 70)
    
    # Initialize Neo4j client
    if neo4j_uri and neo4j_username and neo4j_password:
        client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
        client.create_indexes()
        print("✅ Neo4j client initialized")
    else:
        print("⚠️  No Neo4j credentials - running in dry-run mode")
        client = None
    
    # Read CSV
    print(f"\n📊 Reading CSV: {csv_file}")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"✅ Read {len(rows):,} rows")
    
    # Track what we've processed to avoid duplicates
    systems_created: Set[str] = set()
    assemblies_created: Set[str] = set()
    components_created: Set[str] = set()
    
    # Statistics
    stats = {
        'systems': 0,
        'assemblies': 0,
        'components': 0,
        'errors': 0,
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
        
        # Create system if not already created
        if system_code not in systems_created and client:
            try:
                client.create_system(
                    code=system_code,
                    name=f"System {system_code}",
                    description=f"VMRS System {system_code}"
                )
                systems_created.add(system_code)
                stats['systems'] += 1
            except Exception as e:
                print(f"  ⚠️  Error creating system {system_code}: {e}")
                stats['errors'] += 1
        
        # Create assembly if not already created
        if assembly_code not in assemblies_created and client:
            try:
                client.create_assembly(
                    code=assembly_code,
                    name=f"Assembly {assembly_code}",
                    parent_system_code=system_code,
                    description=f"VMRS Assembly {assembly_code}"
                )
                assemblies_created.add(assembly_code)
                stats['assemblies'] += 1
            except Exception as e:
                print(f"  ⚠️  Error creating assembly {assembly_code}: {e}")
                stats['errors'] += 1
        
        # Create component
        if component_code not in components_created and client:
            try:
                client.create_component(
                    code=component_code,
                    name=description or f"Component {component_code}",
                    parent_assembly_code=assembly_code,
                    description=description
                )
                components_created.add(component_code)
                stats['components'] += 1
            except Exception as e:
                print(f"  ⚠️  Error creating component {component_code}: {e}")
                stats['errors'] += 1
    
    # Fix any missing relationships
    if client:
        print(f"\n🔧 Fixing missing relationships...")
        client.fix_missing_relationships()
    
    # Print statistics
    print(f"\n" + "=" * 70)
    print("📊 IMPORT STATISTICS")
    print("=" * 70)
    print(f"Systems created: {stats['systems']}")
    print(f"Assemblies created: {stats['assemblies']}")
    print(f"Components created: {stats['components']:,}")
    print(f"Skipped rows: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    
    if client:
        neo4j_stats = client.get_statistics()
        print(f"\n📊 Neo4j Statistics:")
        print(f"  Systems: {neo4j_stats.get('systems', 0)}")
        print(f"  Assemblies: {neo4j_stats.get('assemblies', 0)}")
        print(f"  Components: {neo4j_stats.get('components', 0)}")
        print(f"  Relationships: {neo4j_stats.get('total_relationships', 0)}")
    
    print(f"\n✅ Import complete!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import VMRS hierarchy from deduplicated CSV to Neo4j')
    parser.add_argument('--csv', 
                       default='csv data/VMRS_COMPLETE_v20_MASTER_deduplicated.csv',
                       help='Path to deduplicated VMRS CSV file')
    parser.add_argument('--skip-neo4j', action='store_true',
                       help='Skip Neo4j import (dry-run mode)')
    
    args = parser.parse_args()
    
    # Get Neo4j credentials
    neo4j_uri = None
    neo4j_username = None
    neo4j_password = None
    
    if not args.skip_neo4j:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    # Run import
    import_hierarchy_to_neo4j(
        csv_file=args.csv,
        neo4j_uri=neo4j_uri,
        neo4j_username=neo4j_username,
        neo4j_password=neo4j_password
    )


if __name__ == "__main__":
    main()

