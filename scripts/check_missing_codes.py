"""
Check if the 'missing' VMRS codes from acceptance tests exist in Neo4j.

These codes exist in vendor CSV but not in VMRS master CSV.
They should have been created by fix_orphaned_vendor_parts.py
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Codes that were "Not Found" in acceptance tests
CODES_TO_CHECK = [
    '001-004-064',  # VENT - CAB EXHAUSTER, SLEEPER
    '002-017-014',  # SILL - OUTER
    '032-001-001',  # BATTERY
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    print("=== Checking Missing Codes in Neo4j ===\n")

    with driver.session() as session:
        for code in CODES_TO_CHECK:
            # Check if Component exists
            result = session.run("""
                MATCH (c:Component {code: $code})
                OPTIONAL MATCH (c)-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)
                OPTIONAL MATCH (vp:VendorPart)-[:MAPS_TO]->(c)
                RETURN c.code as code,
                       c.name as name,
                       c.source as source,
                       a.code as assembly_code,
                       a.name as assembly_name,
                       s.code as system_code,
                       s.name as system_name,
                       count(vp) as vendor_part_count
            """, code=code)

            record = result.single()

            print(f"Code: {code}")
            if record and record['code']:
                print(f"  Status: FOUND")
                print(f"  Name: {record['name']}")
                print(f"  Source: {record['source'] or 'vmrs_handbook'}")
                print(f"  Assembly: {record['assembly_code']} - {record['assembly_name']}")
                print(f"  System: {record['system_code']} - {record['system_name']}")
                print(f"  VendorParts linked: {record['vendor_part_count']}")
            else:
                print(f"  Status: NOT FOUND")

                # Check if Assembly exists
                assembly_code = code[:7]  # e.g., '001-004'
                assembly_result = session.run("""
                    MATCH (a:Assembly {code: $code})
                    RETURN a.code, a.name
                """, code=assembly_code)
                assembly_record = assembly_result.single()

                if assembly_record:
                    print(f"  Assembly {assembly_code} exists: YES")
                else:
                    print(f"  Assembly {assembly_code} exists: NO (needs to be created first)")

            print()

    driver.close()
    print("Done!")


if __name__ == "__main__":
    main()
