#!/usr/bin/env python3
"""
Minimal runner to ingest EEC graph from a specified text file.
Defaults: temporal/schema processing OFF.

Usage examples:
  PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
    --input /Users/thuptenwangpo/Documents/GitHub/graph-data-modeling-PoC/data/input/smile80.txt

  # Resume from a later chunk
  PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
    --input data/input/smile80.txt --start-chunk 100

Enable temporal/schema later with --with-temporal-schema if needed.
"""

import os
import argparse
from dotenv import load_dotenv
from src.graph_builder import ManualGraphBuilder


def main():
    parser = argparse.ArgumentParser(description="Ingest EEC graph from a specific input text file")
    parser.add_argument("--input", required=True, help="Path to input .txt manual")
    parser.add_argument("--start-chunk", type=int, default=0, help="Starting chunk index (default: 0)")
    parser.add_argument("--with-temporal-schema", action="store_true",
                        help="Also extract temporal patterns and induce schemas (default: off)")
    parser.add_argument("--save-every", type=int, default=1,
                        help="Save progress every N chunks (default: 1)")
    parser.add_argument("--skip-neo4j", action="store_true",
                        help="Skip Neo4j import during extraction (extract to JSON only, import later)")
    args = parser.parse_args()

    print("🚀 Starting EEC ingestion from file")
    print(f"📖 Input: {args.input}")
    if args.start_chunk > 0:
        print(f"📍 Starting from chunk {args.start_chunk}")

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set ANTHROPIC_API_KEY in .env file")
        return

    # Archive existing output files before starting
    print("📦 Archiving existing output files...")
    archive_dir = ManualGraphBuilder.archive_existing_outputs()
    if archive_dir:
        print(f"✅ Archived existing files to: {archive_dir}")

    # Skip Neo4j if flag is set
    if args.skip_neo4j:
        print("⚠️  Running without Neo4j (JSON export only)")
        builder = ManualGraphBuilder(
            anthropic_api_key=api_key,
            neo4j_uri=None,
            neo4j_username=None,
            neo4j_password=None
        )
    else:
        builder = ManualGraphBuilder(
            anthropic_api_key=api_key,
            neo4j_uri=os.getenv("NEO4J_URI"),
            neo4j_username=os.getenv("NEO4J_USERNAME"),
            neo4j_password=os.getenv("NEO4J_PASSWORD")
        )

    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return

    try:
        result = builder.build_graph_from_manual(
            file_path=args.input,
            start_chunk=args.start_chunk,
            process_temporal_schema=args.with_temporal_schema,
            save_every=max(1, args.save_every)
        )

        print("\n✅ EEC Graph ingestion completed!")
        print("📊 Statistics:")
        print(f"  - Total chunks processed: {result['total_chunks']}")
        print(f"  - EEC documents created: {result['total_eec_documents']}")
        print(f"  - Total entities extracted: {result['total_entities']}")
        print(f"  - Total events extracted: {result['total_events']}")
        print(f"  - Total concepts extracted: {result['total_concepts']}")
        print(f"  - Total relationships: {result['total_relationships']}")

        # Export EEC JSON snapshot
        if result['eec_documents']:
            builder.export_eec_json(result['eec_documents'], "knowledge_graph.json")
            print(f"📄 EEC graph exported to: {builder.output_dir}/knowledge_graph.json")

        # Optional temporal/schema prints
        if result.get('temporal_patterns') is not None:
            tp = result['temporal_patterns']
            print(f"\n🔄 Temporal Patterns:")
            print(f"  - Diagnostic sequences: {len(tp['diagnostic_sequences'])}")
            print(f"  - Causal chains: {len(tp['causal_chains'])}")
            print(f"  - Prerequisite graphs: {len(tp['prerequisite_graphs'])}")
            print(f"  - Conditional logic: {len(tp['conditional_logic'])}")

        if result.get('schemas') is not None:
            schemas = result['schemas']
            print(f"\n🏗️ Schemas:")
            print(f"  - Entity hierarchies: {len(schemas['entity_hierarchies'])}")
            print(f"  - Event patterns: {len(schemas['event_patterns'])}")
            print(f"  - Concept networks: {len(schemas['concept_networks'])}")
            print(f"  - Domain schemas: {len(schemas['domain_schemas'])}")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        print("Verify .env configuration and dependencies (pip install -r requirements.txt)")


if __name__ == "__main__":
    main()
