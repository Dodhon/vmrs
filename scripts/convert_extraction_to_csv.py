#!/usr/bin/env python3
"""
Convert triple extraction JSON outputs to CSV files.

Usage:
  PYTHONPATH=. python3 scripts/convert_extraction_to_csv.py
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime


def convert_json_to_csv(json_path: Path, output_dir: Path, run_name: str):
    """
    Convert extraction JSON to CSV files for systems, assemblies, and components.
    
    Args:
        json_path: Path to input JSON file
        output_dir: Directory to save CSV files
        run_name: Name identifier for the run (e.g., "previous", "current")
    """
    print(f"📥 Loading {json_path}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert systems
    systems = data.get('systems', [])
    if systems:
        systems_file = output_dir / f"{run_name}_systems.csv"
        with open(systems_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['code', 'name', 'description'])
            writer.writeheader()
            for system in systems:
                writer.writerow({
                    'code': system.get('code', ''),
                    'name': system.get('name', ''),
                    'description': system.get('description', '')
                })
        print(f"✅ Saved {len(systems)} systems to {systems_file}")
    
    # Convert assemblies
    assemblies = data.get('assemblies', [])
    if assemblies:
        assemblies_file = output_dir / f"{run_name}_assemblies.csv"
        with open(assemblies_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['code', 'name', 'parent_system_code', 'description'])
            writer.writeheader()
            for assembly in assemblies:
                writer.writerow({
                    'code': assembly.get('code', ''),
                    'name': assembly.get('name', ''),
                    'parent_system_code': assembly.get('parent_system_code', ''),
                    'description': assembly.get('description', '')
                })
        print(f"✅ Saved {len(assemblies)} assemblies to {assemblies_file}")
    
    # Convert components
    components = data.get('components', [])
    if components:
        components_file = output_dir / f"{run_name}_components.csv"
        with open(components_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['code', 'name', 'parent_assembly_code', 'description'])
            writer.writeheader()
            for component in components:
                writer.writerow({
                    'code': component.get('code', ''),
                    'name': component.get('name', ''),
                    'parent_assembly_code': component.get('parent_assembly_code', ''),
                    'description': component.get('description', '')
                })
        print(f"✅ Saved {len(components)} components to {components_file}")
    
    # Summary
    print(f"\n📊 Summary for {run_name}:")
    print(f"  Systems: {len(systems)}")
    print(f"  Assemblies: {len(assemblies)}")
    print(f"  Components: {len(components)}")


def main():
    parser = argparse.ArgumentParser(description="Convert extraction JSON to CSV")
    parser.add_argument('--previous', 
                       default='knowledge_graph_output/archive_20251111_194648/knowledge_graph_20251111_175715.json',
                       help='Path to previous extraction JSON')
    parser.add_argument('--current',
                       default='knowledge_graph_output/run_20251111_194658/knowledge_graph_20251111_195654.json',
                       help='Path to current extraction JSON')
    parser.add_argument('--output-dir',
                       default='llm_matching/outputs',
                       help='Output directory for CSV files')
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    print("🔄 Converting extraction runs to CSV...\n")
    
    # Convert previous run
    previous_path = Path(args.previous)
    if previous_path.exists():
        print("=" * 60)
        print("PREVIOUS RUN")
        print("=" * 60)
        convert_json_to_csv(previous_path, output_dir, "previous")
    else:
        print(f"❌ Previous run file not found: {previous_path}")
    
    print("\n")
    
    # Convert current run
    current_path = Path(args.current)
    if current_path.exists():
        print("=" * 60)
        print("CURRENT RUN")
        print("=" * 60)
        convert_json_to_csv(current_path, output_dir, "current")
    else:
        print(f"❌ Current run file not found: {current_path}")
    
    print("\n✅ Conversion complete!")


if __name__ == "__main__":
    main()

