#!/usr/bin/env python3
"""
Import knowledge_graph_output/knowledge_graph.json into Neo4j.

Usage:
  PYTHONPATH=. python scripts/neo4j_import.py knowledge_graph_output/knowledge_graph.json
"""

import json
import os
import sys
from dotenv import load_dotenv

from src.neo4j_client import Neo4jClient


def main():
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. python scripts/neo4j_import.py <path-to-json>")
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        sys.exit(1)

    load_dotenv()

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    if not (uri and user and password):
        print("❌ Missing Neo4j credentials. Please set NEO4J_URI, NEO4J_USERNAME (or NEO4J_USER), NEO4J_PASSWORD in .env")
        sys.exit(1)

    print(f"🔌 Connecting to Neo4j at {uri} as {user}")
    client = Neo4jClient(uri, user, password)
    client.create_indexes()

    print(f"📥 Loading JSON: {json_path}")
    data = json.load(open(json_path))

    systems = data.get("systems", [])
    assemblies = data.get("assemblies", [])
    components = data.get("components", [])

    print(f"🚚 Importing: {len(systems)} systems, {len(assemblies)} assemblies, {len(components)} components")

    # Import systems
    for s in systems:
        client.create_system(
            code=s.get("code", ""),
            name=s.get("name", ""),
            description=s.get("description", "")
        )

    # Import assemblies
    for a in assemblies:
        client.create_assembly(
            code=a.get("code", ""),
            name=a.get("name", ""),
            parent_system_code=a.get("parent_system_code", ""),
            description=a.get("description", "")
        )

    # Import components
    for c in components:
        client.create_component(
            code=c.get("code", ""),
            name=c.get("name", ""),
            parent_assembly_code=c.get("parent_assembly_code", ""),
            description=c.get("description", "")
        )

    # Fix any missing relationships (in case parents were created after children)
    print("🔧 Fixing missing relationships...")
    client.fix_missing_relationships()

    stats = client.get_statistics()
    print("\n✅ Import complete!")
    print(f"Nodes: systems={stats.get('systems', 0)}, assemblies={stats.get('assemblies', 0)}, components={stats.get('components', 0)}")
    print(f"Relationships: {stats.get('total_relationships', 0)}")

    client.close()


if __name__ == "__main__":
    main()
