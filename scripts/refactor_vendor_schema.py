"""
Refactor Neo4j schema to separate vendor parts from VMRS components.

Creates VendorPart nodes and establishes:
- VendorPart -[:MAPS_TO]-> Component
- Vendor -[:MANUFACTURES]-> VendorPart

Removes vendor data from Component nodes and old Vendor->Component relationships.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

VENDOR_CSV = "vendor data/checked/Motors Part Cleanup - Return Data.csv"


def run_query(driver, query, params=None):
    with driver.session() as session:
        result = session.run(query, params or {})
        return result.data()


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    # Load vendor data
    print(f"Loading vendor data from {VENDOR_CSV}...")
    df = pd.read_csv(VENDOR_CSV)
    print(f"Loaded {len(df)} vendor parts")
    
    # Step 1: Delete old Vendor->Component MANUFACTURES relationships
    print("\n1. Deleting old Vendor->Component MANUFACTURES relationships...")
    result = run_query(driver, """
        MATCH (v:Vendor)-[r:MANUFACTURES]->(c:Component)
        DELETE r
        RETURN count(r) as deleted
    """)
    print(f"   Deleted {result[0]['deleted']} relationships")
    
    # Step 2: Remove vendor properties from Component nodes
    print("\n2. Removing vendor properties from Component nodes...")
    run_query(driver, """
        MATCH (c:Component)
        REMOVE c.manufacturers, c.vendor_part_numbers, c.vendor_descriptions, 
               c.part_count, c.manf_codes, c.has_vendor_data
    """)
    print("   Done")
    
    # Step 3: Create VendorPart index
    print("\n3. Creating index on VendorPart.part...")
    try:
        run_query(driver, "CREATE INDEX vendor_part_idx IF NOT EXISTS FOR (vp:VendorPart) ON (vp.part)")
    except Exception as e:
        print(f"   Index may already exist: {e}")
    
    # Step 4: Create VendorPart nodes and relationships in batches
    print("\n4. Creating VendorPart nodes and relationships...")
    batch_size = 500
    total = len(df)
    
    for i in range(0, total, batch_size):
        batch = df.iloc[i:i+batch_size]
        parts = []
        for _, row in batch.iterrows():
            parts.append({
                "part": str(row.get("PART", "")),
                "description": str(row.get("DESCRIPTION", "")),
                "manf_partmfr": str(row.get("MANF_PARTMFR", "")),
                "manf_partmfr_name": str(row.get("MANF_PARTMFR_NAME", "")),
                "manf_partnumber": str(row.get("MANF_PARTNUMBER", "")),
                "vmrs": str(row.get("VMRS", "")),
                "system": str(row.get("SYSTEM_", "")),
                "assembly": str(row.get("ASSEMBLY_", "")),
                "component": str(row.get("COMPONENT_", ""))
            })
        
        # Create VendorPart nodes and MAPS_TO relationships
        run_query(driver, """
            UNWIND $parts AS p
            MERGE (vp:VendorPart {part: p.part})
            SET vp.description = p.description,
                vp.manf_partmfr = p.manf_partmfr,
                vp.manf_partmfr_name = p.manf_partmfr_name,
                vp.manf_partnumber = p.manf_partnumber,
                vp.vmrs = p.vmrs,
                vp.system = p.system,
                vp.assembly = p.assembly,
                vp.component = p.component
            WITH vp, p
            MATCH (c:Component {code: p.vmrs})
            MERGE (vp)-[:MAPS_TO]->(c)
        """, {"parts": parts})
        
        print(f"   Processed {min(i + batch_size, total)}/{total} parts")
    
    # Step 5: Create Vendor->VendorPart MANUFACTURES relationships
    print("\n5. Creating Vendor->VendorPart MANUFACTURES relationships...")
    run_query(driver, """
        MATCH (vp:VendorPart)
        WHERE vp.manf_partmfr IS NOT NULL AND vp.manf_partmfr <> ''
        MATCH (v:Vendor {code: vp.manf_partmfr})
        MERGE (v)-[:MANUFACTURES]->(vp)
    """)
    print("   Done")
    
    # Step 6: Print summary
    print("\n6. Schema summary:")
    counts = run_query(driver, """
        MATCH (vp:VendorPart) 
        OPTIONAL MATCH (vp)-[m:MAPS_TO]->(c:Component)
        OPTIONAL MATCH (v:Vendor)-[mf:MANUFACTURES]->(vp)
        RETURN count(DISTINCT vp) as vendor_parts,
               count(DISTINCT m) as maps_to_rels,
               count(DISTINCT mf) as manufactures_rels
    """)
    print(f"   VendorPart nodes: {counts[0]['vendor_parts']}")
    print(f"   MAPS_TO relationships: {counts[0]['maps_to_rels']}")
    print(f"   MANUFACTURES relationships: {counts[0]['manufactures_rels']}")
    
    driver.close()
    print("\nDone!")


if __name__ == "__main__":
    main()


