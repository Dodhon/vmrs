#!/usr/bin/env python3
"""
Fix Vendor node names in Neo4j.

This script:
1. Reads the vendor CSV to build correct code → name mapping
2. Updates all Vendor nodes with correct manufacturer names
3. Uses MANF_PARTMFR (code) → MANF_PARTMFR_NAME (actual manufacturer)
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.neo4j_client import Neo4jClient

# Load environment variables
load_dotenv()


def fix_vendor_names():
    """Fix vendor names in Neo4j using correct manufacturer names."""
    print("🔧 Fixing Vendor Names in Neo4j")
    print("=" * 70)
    
    # File path
    vendor_file = 'vendor data/checked/Motors Part Cleanup - Return Data.csv'
    
    # Step 1: Load vendor data and build mapping
    print(f"\n📊 Loading vendor data from: {vendor_file}")
    vendor_df = pd.read_csv(vendor_file, encoding='utf-8')
    print(f"✅ Loaded {len(vendor_df):,} vendor parts")
    
    # Build mapping: MANF_PARTMFR (code) → MANF_PARTMFR_NAME (actual manufacturer)
    print(f"\n🔄 Building code → manufacturer name mapping...")
    
    # Get unique code → name pairs
    mapping_df = vendor_df[['MANF_PARTMFR', 'MANF_PARTMFR_NAME']].dropna()
    mapping_df = mapping_df.drop_duplicates()
    
    # Convert to dictionary
    code_to_name = {}
    for _, row in mapping_df.iterrows():
        code = str(row['MANF_PARTMFR']).strip()
        name = str(row['MANF_PARTMFR_NAME']).strip()
        
        if code and name and code != 'nan' and name != 'nan':
            # If we already have this code, verify consistency
            if code in code_to_name and code_to_name[code] != name:
                print(f"⚠️  WARNING: Code '{code}' has multiple names:")
                print(f"   Existing: {code_to_name[code]}")
                print(f"   Found: {name}")
            else:
                code_to_name[code] = name
    
    print(f"✅ Built mapping for {len(code_to_name):,} unique manufacturer codes")
    
    # Initialize Neo4j client
    print(f"\n🔌 Connecting to Neo4j...")
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not all([neo4j_uri, neo4j_username, neo4j_password]):
        print("⚠️  Missing Neo4j credentials in .env file")
        sys.exit(1)
    
    client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
    print("✅ Neo4j client initialized")
    
    # Get current vendor nodes
    print(f"\n📊 Reading current Vendor nodes from Neo4j...")
    with client.driver.session() as session:
        result = session.run("MATCH (v:Vendor) RETURN v.code as code, v.name as name")
        current_vendors = list(result)
    
    print(f"✅ Found {len(current_vendors):,} Vendor nodes")
    
    # Update vendor names
    print(f"\n🔄 Updating Vendor node names...")
    
    updated = 0
    not_found = 0
    unchanged = 0
    
    with client.driver.session() as session:
        for vendor in current_vendors:
            code = vendor['code']
            current_name = vendor['name']
            
            if code in code_to_name:
                correct_name = code_to_name[code]
                
                if current_name != correct_name:
                    # Update the vendor name
                    session.run("""
                        MATCH (v:Vendor {code: $code})
                        SET v.name = $correct_name,
                            v.updated_at = timestamp()
                    """, code=code, correct_name=correct_name)
                    
                    updated += 1
                    if updated <= 10:  # Show first 10 updates
                        print(f"  ✏️  {code}: '{current_name}' → '{correct_name}'")
                else:
                    unchanged += 1
            else:
                not_found += 1
                if not_found <= 5:  # Show first 5 not found
                    print(f"  ⚠️  Code '{code}' not found in vendor data (keeping current name)")
    
    # Get updated statistics
    print(f"\n📊 Getting updated vendor statistics...")
    with client.driver.session() as session:
        # Count unique vendor names (check for remaining duplicates)
        result = session.run("""
            MATCH (v:Vendor)
            WITH v.name as name, collect(v.code) as codes, count(*) as code_count
            WHERE code_count > 1
            RETURN count(*) as duplicate_names
        """)
        duplicate_names = result.single()['duplicate_names']
        
        # Total vendors
        result = session.run("MATCH (v:Vendor) RETURN count(v) as total")
        total_vendors = result.single()['total']
    
    # Print summary
    print(f"\n" + "=" * 70)
    print("📊 UPDATE SUMMARY")
    print("=" * 70)
    print(f"Total vendor nodes: {total_vendors:,}")
    print(f"Names updated: {updated:,}")
    print(f"Names unchanged: {unchanged:,}")
    print(f"Codes not found in source: {not_found:,}")
    print(f"Vendor names with duplicate codes: {duplicate_names:,}")
    
    print(f"\n✅ Vendor name fix complete!")


if __name__ == "__main__":
    fix_vendor_names()

