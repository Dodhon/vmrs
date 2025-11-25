#!/usr/bin/env python3
"""
Import enriched VMRS data (with vendor metadata) to Neo4j.

This script:
1. Reads vmrs_codes_enriched_with_vendor_data.csv
2. Parses 9d codes to extract system, assembly, component
3. Creates System, Assembly, Component nodes with vendor metadata
4. Creates PART_OF relationships
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


def import_enriched_vmrs_to_neo4j(csv_file: str,
                                   neo4j_uri: str = None,
                                   neo4j_username: str = None,
                                   neo4j_password: str = None):
    """
    Import enriched VMRS data from CSV to Neo4j.
    
    Args:
        csv_file: Path to vmrs_codes_enriched_with_vendor_data.csv
        neo4j_uri: Neo4j connection URI
        neo4j_username: Neo4j username
        neo4j_password: Neo4j password
    """
    print("🚀 Enriched VMRS Data Import to Neo4j")
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
        'components_with_vendor_data': 0,
        'errors': 0,
        'skipped': 0
    }
    
    print(f"\n🔄 Processing rows...")
    
    # Process each row
    for i, row in enumerate(rows):
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1:,}/{len(rows):,} rows...")
        
        vmrs_code = row.get('vmrs_code', '').strip()
        vmrs_official_description = row.get('vmrs_official_description', '').strip()
        
        # Vendor metadata
        vendor_part_numbers = row.get('vendor_part_numbers', '').strip()
        vendor_descriptions = row.get('vendor_descriptions', '').strip()
        manufacturers = row.get('manufacturers', '').strip()
        manf_codes = row.get('manf_codes', '').strip()
        part_count = row.get('part_count', '').strip()
        system_name = row.get('system_name', '').strip()
        assembly_name = row.get('assembly_name', '').strip()
        component_name = row.get('component_name', '').strip()
        
        if not vmrs_code:
            stats['skipped'] += 1
            continue
        
        # Parse code_9d to get system, assembly, component
        system_code, assembly_code, component_code = parse_code_9d(vmrs_code)
        
        if not system_code:
            stats['skipped'] += 1
            continue
        
        # Create system if not already created
        if system_code not in systems_created and client:
            try:
                client.create_system(
                    code=system_code,
                    name=system_name or f"System {system_code}",
                    description=system_name or f"VMRS System {system_code}"
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
                    name=assembly_name or f"Assembly {assembly_code}",
                    parent_system_code=system_code,
                    description=assembly_name or f"VMRS Assembly {assembly_code}"
                )
                assemblies_created.add(assembly_code)
                stats['assemblies'] += 1
            except Exception as e:
                print(f"  ⚠️  Error creating assembly {assembly_code}: {e}")
                stats['errors'] += 1
        
        # Create component with vendor metadata
        if component_code not in components_created and client:
            try:
                # Use custom Cypher to add vendor metadata as properties
                with client.driver.session() as session:
                    session.run("""
                        MERGE (c:Component {code: $code})
                        SET c.name = $name,
                            c.description = $description,
                            c.vmrs_official_description = $vmrs_official_description,
                            c.vendor_part_numbers = $vendor_part_numbers,
                            c.vendor_descriptions = $vendor_descriptions,
                            c.manufacturers = $manufacturers,
                            c.manf_codes = $manf_codes,
                            c.part_count = $part_count,
                            c.has_vendor_data = $has_vendor_data,
                            c.updated_at = timestamp()
                        
                        WITH c
                        MATCH (a:Assembly {code: $parent_assembly_code})
                        MERGE (c)-[:PART_OF]->(a)
                        
                        RETURN c
                    """, 
                    code=component_code,
                    name=component_name or vmrs_official_description or f"Component {component_code}",
                    description=vmrs_official_description,
                    vmrs_official_description=vmrs_official_description,
                    vendor_part_numbers=vendor_part_numbers,
                    vendor_descriptions=vendor_descriptions,
                    manufacturers=manufacturers,
                    manf_codes=manf_codes,
                    part_count=part_count if part_count else None,
                    has_vendor_data=bool(vendor_part_numbers),
                    parent_assembly_code=assembly_code)
                
                components_created.add(component_code)
                stats['components'] += 1
                
                if vendor_part_numbers:
                    stats['components_with_vendor_data'] += 1
                    
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
    print(f"Components with vendor data: {stats['components_with_vendor_data']:,}")
    print(f"Components without vendor data: {stats['components'] - stats['components_with_vendor_data']:,}")
    print(f"Skipped rows: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    
    if client:
        neo4j_stats = client.get_statistics()
        print(f"\n📊 Neo4j Statistics:")
        print(f"  Systems: {neo4j_stats.get('systems', 0)}")
        print(f"  Assemblies: {neo4j_stats.get('assemblies', 0)}")
        print(f"  Components: {neo4j_stats.get('components', 0)}")
        print(f"  Relationships: {neo4j_stats.get('total_relationships', 0)}")
        
        # Query components with vendor data
        with client.driver.session() as session:
            result = session.run("""
                MATCH (c:Component)
                WHERE c.has_vendor_data = true
                RETURN count(c) as vendor_enriched_count
            """)
            record = result.single()
            if record:
                print(f"  Components with vendor data: {record['vendor_enriched_count']}")
    
    print(f"\n✅ Import complete!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import enriched VMRS data to Neo4j')
    parser.add_argument('--csv', 
                       default='knowledge_graph_output/vmrs_codes_enriched_with_vendor_data.csv',
                       help='Path to enriched VMRS CSV file')
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
        
        if not all([neo4j_uri, neo4j_username, neo4j_password]):
            print("⚠️  Missing Neo4j credentials in .env file")
            print("Required: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
            sys.exit(1)
    
    # Run import
    import_enriched_vmrs_to_neo4j(
        csv_file=args.csv,
        neo4j_uri=neo4j_uri,
        neo4j_username=neo4j_username,
        neo4j_password=neo4j_password
    )


if __name__ == "__main__":
    main()

