"""
Fix orphaned VendorPart nodes by creating missing Component nodes.

This script:
1. Identifies VendorPart nodes not connected to any Component
2. Creates missing Component nodes using vendor data as source
3. Establishes MAPS_TO relationships
4. Exports unclassified parts (vmrs='nan') for review
"""

import os
import csv
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

OUTPUT_DIR = "eda"


def run_query(driver, query, params=None):
    with driver.session() as session:
        result = session.run(query, params or {})
        return result.data()


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    # Step 1: Get baseline counts
    print("=== Baseline Counts ===")
    baseline = run_query(driver, """
        MATCH (vp:VendorPart)
        OPTIONAL MATCH (vp)-[m:MAPS_TO]->(c:Component)
        RETURN count(vp) as total_parts,
               count(m) as linked_parts,
               count(vp) - count(m) as orphaned_parts
    """)[0]
    print(f"Total VendorParts: {baseline['total_parts']}")
    print(f"Linked to Components: {baseline['linked_parts']}")
    print(f"Orphaned: {baseline['orphaned_parts']}")
    
    # Step 2: Find missing Component codes (exclude 'nan')
    print("\n=== Finding Missing Component Codes ===")
    missing_codes = run_query(driver, """
        MATCH (vp:VendorPart)
        WHERE NOT (vp)-[:MAPS_TO]->(:Component)
          AND vp.vmrs <> 'nan' AND vp.vmrs IS NOT NULL AND vp.vmrs <> ''
        WITH vp.vmrs as code, 
             collect(DISTINCT vp.component)[0] as component_name,
             substring(vp.vmrs, 0, 7) as assembly_code,
             count(*) as part_count
        RETURN code, component_name, assembly_code, part_count
        ORDER BY part_count DESC
    """)
    print(f"Found {len(missing_codes)} unique VMRS codes to create")
    
    # Step 3: Create missing Component nodes and link to Assemblies
    print("\n=== Creating Missing Components ===")
    created = run_query(driver, """
        MATCH (vp:VendorPart)
        WHERE NOT (vp)-[:MAPS_TO]->(:Component)
          AND vp.vmrs <> 'nan' AND vp.vmrs IS NOT NULL AND vp.vmrs <> ''
        WITH vp.vmrs as code, 
             collect(DISTINCT vp.component)[0] as component_name,
             substring(vp.vmrs, 0, 7) as assembly_code
        MATCH (a:Assembly {code: assembly_code})
        MERGE (c:Component {code: code})
        ON CREATE SET c.name = component_name, c.source = 'vendor_data'
        MERGE (c)-[:PART_OF]->(a)
        RETURN count(DISTINCT c) as components_created
    """)
    print(f"Created {created[0]['components_created']} Component nodes")
    
    # Step 4: Create MAPS_TO relationships for previously orphaned parts
    print("\n=== Creating MAPS_TO Relationships ===")
    linked = run_query(driver, """
        MATCH (vp:VendorPart)
        WHERE NOT (vp)-[:MAPS_TO]->(:Component)
          AND vp.vmrs <> 'nan' AND vp.vmrs IS NOT NULL AND vp.vmrs <> ''
        MATCH (c:Component {code: vp.vmrs})
        MERGE (vp)-[:MAPS_TO]->(c)
        RETURN count(*) as relationships_created
    """)
    print(f"Created {linked[0]['relationships_created']} MAPS_TO relationships")
    
    # Step 5: Export unclassified parts (vmrs='nan')
    print("\n=== Exporting Unclassified Parts ===")
    unclassified = run_query(driver, """
        MATCH (vp:VendorPart)
        WHERE vp.vmrs = 'nan'
        OPTIONAL MATCH (v:Vendor)-[:MANUFACTURES]->(vp)
        RETURN vp.part as part, 
               vp.description as description,
               vp.manf_partmfr_name as manufacturer,
               v.name as vendor_name
        ORDER BY vp.description
    """)
    
    output_file = os.path.join(OUTPUT_DIR, "unclassified_vendor_parts.csv")
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['part', 'description', 'manufacturer', 'vendor_name'])
        writer.writeheader()
        writer.writerows(unclassified)
    print(f"Exported {len(unclassified)} unclassified parts to {output_file}")
    
    # Step 6: Final counts
    print("\n=== Final Counts ===")
    final = run_query(driver, """
        MATCH (vp:VendorPart)
        OPTIONAL MATCH (vp)-[m:MAPS_TO]->(c:Component)
        RETURN count(vp) as total_parts,
               count(m) as linked_parts,
               count(vp) - count(m) as orphaned_parts
    """)[0]
    print(f"Total VendorParts: {final['total_parts']}")
    print(f"Linked to Components: {final['linked_parts']}")
    print(f"Still orphaned (no VMRS): {final['orphaned_parts']}")
    
    # Component counts
    components = run_query(driver, """
        MATCH (c:Component)
        RETURN count(c) as total,
               count(CASE WHEN c.source = 'vendor_data' THEN 1 END) as from_vendor
    """)[0]
    print(f"\nComponent nodes: {components['total']} (from vendor: {components['from_vendor']})")
    
    driver.close()
    print("\nDone!")


if __name__ == "__main__":
    main()




