#!/usr/bin/env python3
"""
Import VMRS data from CSV directly to Neo4j.

This script:
1. Reads VMRS_COMPLETE_v20_MASTER.csv (structured data)
2. Extracts system names from markdown (context/enrichment)
3. Imports Systems, Assemblies, and Components to Neo4j
4. Creates PART_OF relationships
5. Much faster and more accurate than LLM extraction
"""

import csv
import re
import sys
import os
from pathlib import Path
from typing import Dict, Set, Optional
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.neo4j_client import Neo4jClient

# Load environment variables
load_dotenv()


def extract_system_names_from_markdown(md_file: str) -> Dict[str, str]:
    """
    Extract system codes and names from markdown file.
    
    Returns:
        Dictionary mapping system code -> system name
    """
    systems = {}
    
    if not os.path.exists(md_file):
        print(f"⚠️  Markdown file not found: {md_file}")
        return systems
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Code Key 31 section
    ck31_start = content.find("#### Code Key 31: System Codes")
    if ck31_start == -1:
        ck31_start = content.find("Code Key 31: System Codes")
    
    if ck31_start == -1:
        print("⚠️  Code Key 31 section not found in markdown")
        return systems
    
    # Get section (first 100k chars should be enough)
    ck31_section = content[ck31_start:ck31_start+100000]
    
    # Extract system codes and names
    # Pattern 1: "- 013 Brakes" or "- 044 Fuel System"
    pattern1 = r'-\s*(\d{3})\s+([A-Z][^-\n|]{5,80}?)(?:\n|$)'
    # Pattern 2: "| 031 | Charging System |"
    pattern2 = r'\|\s*(\d{3})\s*\|\s*([^|\n]{5,80}?)\s*\|'
    
    for pattern in [pattern1, pattern2]:
        matches = re.finditer(pattern, ck31_section, re.MULTILINE)
        for match in matches:
            code = match.group(1).strip()
            name = match.group(2).strip()
            # Clean up name
            name = re.sub(r'<br>.*', '', name)  # Remove <br> tags and after
            name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
            name = name.rstrip('—').strip()  # Remove trailing dashes
            
            # Validate
            if len(code) == 3 and code.isdigit() and 1 <= int(code) <= 999:
                if len(name) > 3 and len(name) < 100:
                    # Keep longest/best name
                    if code not in systems or len(name) > len(systems[code]):
                        systems[code] = name
    
    return systems


def import_csv_to_neo4j(csv_file: str, md_file: Optional[str] = None,
                        neo4j_uri: Optional[str] = None,
                        neo4j_username: Optional[str] = None,
                        neo4j_password: Optional[str] = None):
    """
    Import VMRS data from CSV to Neo4j.
    
    Args:
        csv_file: Path to VMRS_COMPLETE_v20_MASTER.csv
        md_file: Optional path to markdown file for system names
        neo4j_uri: Neo4j connection URI
        neo4j_username: Neo4j username
        neo4j_password: Neo4j password
    """
    print("🚀 VMRS CSV to Neo4j Import")
    print("=" * 70)
    
    # Initialize Neo4j client
    if neo4j_uri and neo4j_username and neo4j_password:
        client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
        client.create_indexes()
        print("✅ Neo4j client initialized")
    else:
        print("⚠️  No Neo4j credentials - running in dry-run mode")
        client = None
    
    # Extract system names from markdown if available
    system_names = {}
    if md_file and os.path.exists(md_file):
        print(f"\n📖 Extracting system names from: {md_file}")
        system_names = extract_system_names_from_markdown(md_file)
        print(f"✅ Found {len(system_names)} system names")
    else:
        print(f"\n⚠️  No markdown file provided - systems will have codes only")
    
    # Read CSV
    print(f"\n📊 Reading CSV: {csv_file}")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"✅ Read {len(rows):,} rows")
    
    # Track what we've processed
    systems_created = set()
    assemblies_created = set()
    components_created = set()
    
    # Statistics
    stats = {
        'systems': 0,
        'assemblies': 0,
        'components': 0,
        'errors': 0
    }
    
    print(f"\n🔄 Processing rows...")
    
    # Process each row
    for i, row in enumerate(rows):
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1:,}/{len(rows):,} rows...")
        
        system_code = row.get('system', '').strip()
        code_6d = row.get('code_6d', '').strip()
        code_9d = row.get('code_9d', '').strip()
        subcode = row.get('subcode', '').strip()
        description = row.get('description', '').strip()
        
        if not system_code:
            continue
        
        # Validate system code
        if not re.match(r'^\d{3}$', system_code) or not (1 <= int(system_code) <= 999):
            continue
        
        # Create system if not already created
        if system_code not in systems_created and client:
            system_name = system_names.get(system_code, f"System {system_code}")
            try:
                client.create_system(
                    code=system_code,
                    name=system_name,
                    description=f"VMRS System {system_code}"
                )
                systems_created.add(system_code)
                stats['systems'] += 1
            except Exception as e:
                print(f"  ⚠️  Error creating system {system_code}: {e}")
                stats['errors'] += 1
        
        # Create assembly if we have code_6d
        if code_6d and re.match(r'^\d{3}-\d{3}$', code_6d):
            if code_6d not in assemblies_created and client:
                try:
                    # Derive system code from assembly code
                    assembly_system = code_6d.split('-')[0]
                    client.create_assembly(
                        code=code_6d,
                        name=description or f"Assembly {code_6d}",
                        parent_system_code=assembly_system,
                        description=description
                    )
                    assemblies_created.add(code_6d)
                    stats['assemblies'] += 1
                except Exception as e:
                    print(f"  ⚠️  Error creating assembly {code_6d}: {e}")
                    stats['errors'] += 1
        
        # Create component if we have code_9d
        elif code_9d and re.match(r'^\d{3}-\d{3}-\d{3}$', code_9d):
            if code_9d not in components_created and client:
                try:
                    # Derive assembly code from component code
                    parts = code_9d.split('-')
                    assembly_code = f"{parts[0]}-{parts[1]}"
                    client.create_component(
                        code=code_9d,
                        name=description or f"Component {code_9d}",
                        parent_assembly_code=assembly_code,
                        description=description
                    )
                    components_created.add(code_9d)
                    stats['components'] += 1
                except Exception as e:
                    print(f"  ⚠️  Error creating component {code_9d}: {e}")
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
    
    parser = argparse.ArgumentParser(description='Import VMRS CSV to Neo4j')
    parser.add_argument('--csv', default='csv data/VMRS_COMPLETE_v20_MASTER.csv',
                       help='Path to VMRS CSV file')
    parser.add_argument('--md', default='llm_matching/matching_context_cleaned.md',
                       help='Path to markdown file for system names (optional)')
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
    import_csv_to_neo4j(
        csv_file=args.csv,
        md_file=args.md if os.path.exists(args.md) else None,
        neo4j_uri=neo4j_uri,
        neo4j_username=neo4j_username,
        neo4j_password=neo4j_password
    )


if __name__ == "__main__":
    main()


