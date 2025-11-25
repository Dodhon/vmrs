#!/usr/bin/env python3
"""
Create Vendor nodes from Component manufacturer properties.

This script:
1. Reads Components with vendor data
2. Parses concatenated manufacturers/manf_codes
3. Creates Vendor nodes
4. Creates MANUFACTURES relationships from Vendor to Component
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


def create_vendor_nodes_and_relationships():
    """Create Vendor nodes from Component manufacturer properties."""
    print("🚀 Creating Vendor Nodes from Component Properties")
    print("=" * 70)
    
    # Initialize Neo4j client
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not all([neo4j_uri, neo4j_username, neo4j_password]):
        print("⚠️  Missing Neo4j credentials in .env file")
        sys.exit(1)
    
    client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
    print("✅ Neo4j client initialized")
    
    # Create index on Vendor code
    print("\n📊 Creating index on Vendor.code...")
    with client.driver.session() as session:
        session.run("CREATE INDEX vendor_code_index IF NOT EXISTS FOR (v:Vendor) ON (v.code)")
    print("✅ Index created")
    
    # Get all components with vendor data
    print("\n📊 Reading components with vendor data...")
    with client.driver.session() as session:
        result = session.run("""
            MATCH (c:Component)
            WHERE c.has_vendor_data = true
            RETURN c.code as component_code, 
                   c.manufacturers as manufacturers, 
                   c.manf_codes as manf_codes
        """)
        components = list(result)
    
    print(f"✅ Found {len(components):,} components with vendor data")
    
    # Parse and create vendors
    print("\n🔄 Creating Vendor nodes and MANUFACTURES relationships...")
    
    vendors_created = set()
    relationships_created = 0
    
    with client.driver.session() as session:
        for i, comp in enumerate(components):
            if (i + 1) % 1000 == 0:
                print(f"  Processed {i+1:,}/{len(components):,} components...")
            
            component_code = comp['component_code']
            manufacturers = comp.get('manufacturers', '')
            manf_codes = comp.get('manf_codes', '')
            
            if not manufacturers or not manf_codes:
                continue
            
            # Split by " / " delimiter
            mfr_names = [m.strip() for m in manufacturers.split('/')]
            mfr_codes = [c.strip() for c in manf_codes.split('/')]
            
            # Match them up (they should be parallel arrays)
            for name, code in zip(mfr_names, mfr_codes):
                if not name or not code:
                    continue
                
                # Create Vendor node and MANUFACTURES relationship
                session.run("""
                    MERGE (v:Vendor {code: $code})
                    SET v.name = $name,
                        v.updated_at = timestamp()
                    
                    WITH v
                    MATCH (c:Component {code: $component_code})
                    MERGE (v)-[:MANUFACTURES]->(c)
                """, 
                code=code,
                name=name,
                component_code=component_code)
                
                vendors_created.add(code)
                relationships_created += 1
    
    # Get final statistics
    print("\n📊 Getting final statistics...")
    with client.driver.session() as session:
        # Count vendors
        result = session.run("MATCH (v:Vendor) RETURN count(v) as count")
        vendor_count = result.single()['count']
        
        # Count MANUFACTURES relationships
        result = session.run("MATCH ()-[r:MANUFACTURES]->() RETURN count(r) as count")
        manufactures_count = result.single()['count']
        
        # Sample vendors
        result = session.run("""
            MATCH (v:Vendor)-[r:MANUFACTURES]->(c:Component)
            RETURN v.code, v.name, count(c) as component_count
            ORDER BY component_count DESC
            LIMIT 10
        """)
        top_vendors = list(result)
    
    # Print statistics
    print("\n" + "=" * 70)
    print("📊 VENDOR CREATION STATISTICS")
    print("=" * 70)
    print(f"Unique vendors created: {vendor_count}")
    print(f"MANUFACTURES relationships created: {manufactures_count}")
    
    print("\n📊 Top 10 Vendors by Component Count:")
    for vendor in top_vendors:
        print(f"  {vendor['v.code']:6} - {vendor['v.name']:40} ({vendor['component_count']:,} components)")
    
    print("\n✅ Vendor node creation complete!")


if __name__ == "__main__":
    create_vendor_nodes_and_relationships()

