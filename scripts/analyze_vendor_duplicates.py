#!/usr/bin/env python3
"""
Analyze duplicate vendor names in Neo4j.

This script finds vendors that share the same company name but have different codes.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.neo4j_client import Neo4jClient

# Load environment variables
load_dotenv()


def analyze_vendor_duplicates():
    """Find and analyze vendors with duplicate names."""
    print("🔍 Analyzing Vendor Name Duplicates")
    print("=" * 70)
    
    # Initialize Neo4j client
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not all([neo4j_uri, neo4j_username, neo4j_password]):
        print("⚠️  Missing Neo4j credentials in .env file")
        sys.exit(1)
    
    client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
    print("✅ Neo4j client initialized\n")
    
    with client.driver.session() as session:
        # Find duplicate vendor names
        print("📊 Finding vendors with duplicate names...")
        result = session.run("""
            MATCH (v:Vendor)
            WITH v.name as name, collect(v.code) as codes, count(*) as code_count
            WHERE code_count > 1
            RETURN name, codes, code_count
            ORDER BY code_count DESC, name
        """)
        duplicates = list(result)
        
        print(f"✅ Found {len(duplicates)} vendor names with multiple codes\n")
        
        # Display duplicates
        print("=" * 70)
        print("VENDOR NAMES WITH MULTIPLE CODES")
        print("=" * 70)
        
        total_codes = 0
        for dup in duplicates:
            name = dup['name']
            codes = dup['codes']
            count = dup['code_count']
            total_codes += count
            
            print(f"\n{name}")
            print(f"  Codes ({count}): {', '.join(sorted(codes))}")
        
        # Get component counts for each code
        print("\n" + "=" * 70)
        print("DETAILED BREAKDOWN WITH COMPONENT COUNTS")
        print("=" * 70)
        
        for dup in duplicates:
            name = dup['name']
            codes = dup['codes']
            
            print(f"\n📦 {name}")
            
            # Get component count for each code
            for code in sorted(codes):
                result = session.run("""
                    MATCH (v:Vendor {code: $code})-[:MANUFACTURES]->(c:Component)
                    RETURN count(c) as component_count
                """, code=code)
                comp_count = result.single()['component_count']
                print(f"  {code:6} → {comp_count:,} components")
        
        # Summary statistics
        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS")
        print("=" * 70)
        print(f"Vendor names with duplicates: {len(duplicates)}")
        print(f"Total vendor codes in duplicates: {total_codes}")
        print(f"Average codes per duplicate name: {total_codes / len(duplicates):.1f}")
        
        # Overall vendor statistics
        result = session.run("MATCH (v:Vendor) RETURN count(v) as total")
        total_vendors = result.single()['total']
        
        result = session.run("""
            MATCH (v:Vendor)
            RETURN count(DISTINCT v.name) as unique_names
        """)
        unique_names = result.single()['unique_names']
        
        print(f"\nTotal vendor nodes: {total_vendors}")
        print(f"Unique vendor names: {unique_names}")
        print(f"Duplicate rate: {(total_vendors - unique_names) / total_vendors * 100:.1f}%")


if __name__ == "__main__":
    analyze_vendor_duplicates()



