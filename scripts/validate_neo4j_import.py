#!/usr/bin/env python3
"""
Validate Neo4j knowledge graph import.

This script:
1. Queries Neo4j to get actual node and relationship counts
2. Compares with expected counts from JSON metadata
3. Validates data quality (missing relationships, orphaned nodes)
4. Provides validation report and next steps
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.neo4j_client import Neo4jClient

# Load environment variables
load_dotenv()


def validate_neo4j_import(json_file: str = None, neo4j_uri: str = None,
                          neo4j_username: str = None, neo4j_password: str = None):
    """
    Validate Neo4j import against JSON metadata.
    
    Args:
        json_file: Path to knowledge graph JSON file
        neo4j_uri: Neo4j connection URI
        neo4j_username: Neo4j username
        neo4j_password: Neo4j password
    """
    print("=" * 70)
    print("🔍 NEO4J IMPORT VALIDATION")
    print("=" * 70)
    
    # Load JSON metadata
    if json_file:
        json_path = Path(json_file)
    else:
        json_path = Path("knowledge_graph_output/combined_triple_extraction_and_md_tables.json")
    
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return
    
    print(f"\n📥 Loading JSON metadata: {json_path}")
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    metadata = json_data.get('metadata', {})
    expected = {
        'systems': metadata.get('total_systems', 0),
        'assemblies': metadata.get('total_assemblies', 0),
        'components': metadata.get('total_components', 0),
        'relationships': metadata.get('total_relationships', 0)
    }
    
    print(f"\n📊 Expected counts from JSON:")
    print(f"  Systems: {expected['systems']:,}")
    print(f"  Assemblies: {expected['assemblies']:,}")
    print(f"  Components: {expected['components']:,}")
    print(f"  Relationships: {expected['relationships']:,}")
    
    # Connect to Neo4j
    if not neo4j_uri:
        neo4j_uri = os.getenv("NEO4J_URI")
    if not neo4j_username:
        neo4j_username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    if not neo4j_password:
        neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not (neo4j_uri and neo4j_username and neo4j_password):
        print("\n❌ Missing Neo4j credentials. Please set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in .env")
        return
    
    print(f"\n🔌 Connecting to Neo4j at {neo4j_uri}...")
    client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
    
    # Get actual counts
    print("\n📊 Querying Neo4j database...")
    actual = client.get_statistics()
    
    print(f"\n📊 Actual counts in Neo4j:")
    print(f"  Systems: {actual['systems']:,}")
    print(f"  Assemblies: {actual['assemblies']:,}")
    print(f"  Components: {actual['components']:,}")
    print(f"  Vendors: {actual['vendors']:,}")
    print(f"  Relationships: {actual['total_relationships']:,}")
    
    # Compare counts
    print("\n" + "=" * 70)
    print("📈 VALIDATION RESULTS")
    print("=" * 70)
    
    validation_results = {
        'systems': {'expected': expected['systems'], 'actual': actual['systems'], 'match': False},
        'assemblies': {'expected': expected['assemblies'], 'actual': actual['assemblies'], 'match': False},
        'components': {'expected': expected['components'], 'actual': actual['components'], 'match': False},
        'relationships': {'expected': expected['relationships'], 'actual': actual['total_relationships'], 'match': False}
    }
    
    all_match = True
    for entity_type, result in validation_results.items():
        result['match'] = result['expected'] == result['actual']
        status = "✅" if result['match'] else "❌"
        diff = result['actual'] - result['expected']
        diff_str = f" ({diff:+d})" if diff != 0 else ""
        print(f"{status} {entity_type.capitalize()}: Expected {result['expected']:,}, Got {result['actual']:,}{diff_str}")
        if not result['match']:
            all_match = False
    
    # Check for orphaned nodes (nodes without relationships)
    print("\n" + "=" * 70)
    print("🔍 DATA QUALITY CHECKS")
    print("=" * 70)
    
    with client.driver.session() as session:
        # Check orphaned assemblies (no PART_OF relationship)
        orphaned_assemblies = session.run("""
            MATCH (a:Assembly)
            WHERE NOT (a)-[:PART_OF]->()
            RETURN count(a) as count
        """).single()["count"]
        
        # Check orphaned components (no PART_OF relationship)
        orphaned_components = session.run("""
            MATCH (c:Component)
            WHERE NOT (c)-[:PART_OF]->()
            RETURN count(c) as count
        """).single()["count"]
        
        # Check systems with no children
        systems_no_children = session.run("""
            MATCH (s:System)
            WHERE NOT ()-[:PART_OF]->(s)
            RETURN count(s) as count
        """).single()["count"]
        
        # Check relationship types breakdown
        assembly_to_system = session.run("""
            MATCH (a:Assembly)-[:PART_OF]->(s:System)
            RETURN count(*) as count
        """).single()["count"]
        
        component_to_assembly = session.run("""
            MATCH (c:Component)-[:PART_OF]->(a:Assembly)
            RETURN count(*) as count
        """).single()["count"]
    
    print(f"Orphaned assemblies (no PART_OF): {orphaned_assemblies:,}")
    print(f"Orphaned components (no PART_OF): {orphaned_components:,}")
    print(f"Systems with no children: {systems_no_children:,}")
    print(f"\nRelationship breakdown:")
    print(f"  Assembly → System: {assembly_to_system:,}")
    print(f"  Component → Assembly: {component_to_assembly:,}")
    
    # Sample queries to verify data
    print("\n" + "=" * 70)
    print("🔎 SAMPLE DATA VERIFICATION")
    print("=" * 70)
    
    with client.driver.session() as session:
        # Sample system with hierarchy
        sample_system = session.run("""
            MATCH (s:System)
            OPTIONAL MATCH (s)<-[:PART_OF]-(a:Assembly)
            OPTIONAL MATCH (a)<-[:PART_OF]-(c:Component)
            WITH s, count(DISTINCT a) as assembly_count, count(DISTINCT c) as component_count
            WHERE assembly_count > 0
            RETURN s.code as code, s.name as name, assembly_count, component_count
            LIMIT 5
        """).data()
        
        print("\nSample systems with hierarchies:")
        for sys in sample_system:
            print(f"  {sys['code']}: {sys['name']} - {sys['assembly_count']} assemblies, {sys['component_count']} components")
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 VALIDATION SUMMARY")
    print("=" * 70)
    
    if all_match:
        print("✅ All counts match expected values!")
    else:
        print("⚠️  Some counts don't match expected values.")
        print("\nPossible reasons:")
        print("  - Import may have skipped some nodes")
        print("  - Duplicate nodes may have been merged")
        print("  - Some relationships may not have been created")
    
    if orphaned_assemblies > 0 or orphaned_components > 0:
        print(f"\n⚠️  Found {orphaned_assemblies + orphaned_components} orphaned nodes.")
        print("  Run: client.fix_missing_relationships() to fix")
    
    # Close connection
    client.close()
    
    return {
        'validation_passed': all_match,
        'expected': expected,
        'actual': actual,
        'orphaned': {
            'assemblies': orphaned_assemblies,
            'components': orphaned_components
        }
    }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Neo4j knowledge graph import')
    parser.add_argument('--json',
                       default='knowledge_graph_output/combined_triple_extraction_and_md_tables.json',
                       help='Path to knowledge graph JSON file')
    parser.add_argument('--skip-neo4j', action='store_true',
                       help='Skip Neo4j validation (dry-run mode)')
    
    args = parser.parse_args()
    
    if args.skip_neo4j:
        print("⚠️  Running in dry-run mode (skipping Neo4j validation)")
        return
    
    validate_neo4j_import(json_file=args.json)


if __name__ == "__main__":
    main()


