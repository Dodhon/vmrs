#!/usr/bin/env python3
"""
Combine previous and current triple extraction runs into a single knowledge graph.

Usage:
  PYTHONPATH=. python3 scripts/combine_extractions.py
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def combine_descriptions(desc1: str, desc2: str) -> str:
    """Combine two descriptions with separator, handling duplicates."""
    desc1 = desc1.strip() if desc1 else ""
    desc2 = desc2.strip() if desc2 else ""
    
    if not desc1:
        return desc2
    if not desc2:
        return desc1
    if desc1 == desc2:
        return desc1
    
    return f"{desc1} | {desc2}"


def merge_entities(prev_entities: list, current_entities: list, entity_type: str) -> dict:
    """
    Merge entities from previous and current runs.
    
    Returns:
        Dictionary with merged entities and statistics
    """
    prev_by_code = {e['code']: e for e in prev_entities}
    current_by_code = {e['code']: e for e in current_entities}
    
    merged = {}
    stats = {
        'previous': len(prev_entities),
        'current': len(current_entities),
        'overlap': 0,
        'descriptions_combined': 0,
        'names_preserved': 0,
        'parent_codes_preserved': 0
    }
    
    all_codes = set(prev_by_code.keys()) | set(current_by_code.keys())
    
    for code in all_codes:
        prev_entity = prev_by_code.get(code)
        current_entity = current_by_code.get(code)
        
        if prev_entity and current_entity:
            # Both exist - merge
            stats['overlap'] += 1
            
            # Determine primary name (longer, or current if equal)
            prev_name = prev_entity.get('name', '').strip()
            current_name = current_entity.get('name', '').strip()
            
            if len(current_name) > len(prev_name):
                primary_name = current_name
                alternative_name = prev_name if prev_name != current_name else None
            else:
                primary_name = prev_name
                alternative_name = current_name if current_name != prev_name else None
            
            # Combine descriptions
            prev_desc = prev_entity.get('description', '')
            current_desc = current_entity.get('description', '')
            combined_desc = combine_descriptions(prev_desc, current_desc)
            if prev_desc and current_desc and prev_desc != current_desc:
                stats['descriptions_combined'] += 1
            
            # Build merged entity
            merged_entity = {
                'code': code,
                'name': primary_name,
                'description': combined_desc,
                'source': 'both'
            }
            
            # Add alternative name if different
            if alternative_name:
                merged_entity['alternative_names'] = [alternative_name]
                stats['names_preserved'] += 1
            
            # Handle parent codes (for assemblies and components)
            if entity_type == 'assemblies':
                prev_parent = prev_entity.get('parent_system_code', '')
                current_parent = current_entity.get('parent_system_code', '')
                
                if current_parent:
                    merged_entity['parent_system_code'] = current_parent
                    if prev_parent and prev_parent != current_parent:
                        merged_entity['alternative_parent_system_codes'] = [prev_parent]
                        stats['parent_codes_preserved'] += 1
                elif prev_parent:
                    merged_entity['parent_system_code'] = prev_parent
            
            elif entity_type == 'components':
                prev_parent = prev_entity.get('parent_assembly_code', '')
                current_parent = current_entity.get('parent_assembly_code', '')
                
                if current_parent:
                    merged_entity['parent_assembly_code'] = current_parent
                    if prev_parent and prev_parent != current_parent:
                        merged_entity['alternative_parent_assembly_codes'] = [prev_parent]
                        stats['parent_codes_preserved'] += 1
                elif prev_parent:
                    merged_entity['parent_assembly_code'] = prev_parent
            
            merged[code] = merged_entity
            
        elif prev_entity:
            # Only in previous
            entity = prev_entity.copy()
            entity['source'] = 'previous'
            merged[code] = entity
            
        else:
            # Only in current
            entity = current_entity.copy()
            entity['source'] = 'current'
            merged[code] = entity
    
    return {
        'entities': list(merged.values()),
        'stats': stats
    }


def build_related_parts(systems: list, assemblies: list, components: list) -> dict:
    """Build related parts tracking for all entities."""
    # Index entities by code
    systems_by_code = {s['code']: s for s in systems}
    assemblies_by_code = {a['code']: a for a in assemblies}
    components_by_code = {c['code']: c for c in components}
    
    # Build child relationships
    system_children = defaultdict(list)
    assembly_children = defaultdict(list)
    
    for assembly in assemblies:
        parent_sys = assembly.get('parent_system_code', '')
        if parent_sys and parent_sys in systems_by_code:
            system_children[parent_sys].append(assembly['code'])
    
    for component in components:
        parent_asm = component.get('parent_assembly_code', '')
        if parent_asm and parent_asm in assemblies_by_code:
            assembly_children[parent_asm].append(component['code'])
    
    # Add related parts to systems
    for system in systems:
        code = system['code']
        children = system_children.get(code, [])
        system['related_parts'] = {
            'child_assemblies': children,
            'total_children': len(children)
        }
    
    # Add related parts to assemblies
    for assembly in assemblies:
        code = assembly['code']
        parent_sys = assembly.get('parent_system_code', '')
        children = assembly_children.get(code, [])
        
        related = {
            'total_children': len(children)
        }
        
        if parent_sys:
            related['parent_system'] = parent_sys
        
        if children:
            related['child_components'] = children
        
        assembly['related_parts'] = related
    
    # Add related parts to components
    for component in components:
        code = component['code']
        parent_asm = component.get('parent_assembly_code', '')
        
        related = {}
        
        if parent_asm:
            related['parent_assembly'] = parent_asm
            # Get parent system from assembly
            if parent_asm in assemblies_by_code:
                parent_sys = assemblies_by_code[parent_asm].get('parent_system_code', '')
                if parent_sys:
                    related['parent_system'] = parent_sys
            
            # Get sibling components (same parent assembly)
            siblings = [
                c['code'] for c in components
                if c.get('parent_assembly_code') == parent_asm and c['code'] != code
            ]
            if siblings:
                related['sibling_components'] = siblings
        
        component['related_parts'] = related
    
    return {
        'systems': systems,
        'assemblies': assemblies,
        'components': components
    }


def main():
    parser = argparse.ArgumentParser(description="Combine extraction runs")
    parser.add_argument('--previous',
                       default='knowledge_graph_output/archive_20251111_194648/knowledge_graph_20251111_175715.json',
                       help='Path to previous extraction JSON')
    parser.add_argument('--current',
                       default='knowledge_graph_output/run_20251111_194658/knowledge_graph_20251111_195654.json',
                       help='Path to current extraction JSON')
    parser.add_argument('--output-dir',
                       default='knowledge_graph_output',
                       help='Output directory for combined JSON')
    args = parser.parse_args()
    
    # Load previous run
    previous_path = Path(args.previous)
    if not previous_path.exists():
        print(f"❌ Previous run file not found: {previous_path}")
        return
    
    print(f"📥 Loading previous run: {previous_path}")
    with open(previous_path, 'r') as f:
        previous_data = json.load(f)
    
    # Load current run
    current_path = Path(args.current)
    if not current_path.exists():
        print(f"❌ Current run file not found: {current_path}")
        return
    
    print(f"📥 Loading current run: {current_path}")
    with open(current_path, 'r') as f:
        current_data = json.load(f)
    
    print("\n🔄 Merging entities...")
    
    # Merge systems
    systems_result = merge_entities(
        previous_data.get('systems', []),
        current_data.get('systems', []),
        'systems'
    )
    systems = systems_result['entities']
    systems_stats = systems_result['stats']
    
    # Merge assemblies
    assemblies_result = merge_entities(
        previous_data.get('assemblies', []),
        current_data.get('assemblies', []),
        'assemblies'
    )
    assemblies = assemblies_result['entities']
    assemblies_stats = assemblies_result['stats']
    
    # Merge components
    components_result = merge_entities(
        previous_data.get('components', []),
        current_data.get('components', []),
        'components'
    )
    components = components_result['entities']
    components_stats = components_result['stats']
    
    print("🔗 Building related parts...")
    result = build_related_parts(systems, assemblies, components)
    systems = result['systems']
    assemblies = result['assemblies']
    components = result['components']
    
    # Calculate relationships
    assembly_relationships = sum(1 for a in assemblies if a.get('parent_system_code'))
    component_relationships = sum(1 for c in components if c.get('parent_assembly_code'))
    total_relationships = assembly_relationships + component_relationships
    
    # Build output
    output_data = {
        'metadata': {
            'total_systems': len(systems),
            'total_assemblies': len(assemblies),
            'total_components': len(components),
            'total_relationships': total_relationships,
            'extraction_date': datetime.now().isoformat(),
            'sources': {
                'previous': str(previous_path),
                'current': str(current_path)
            },
            'merge_statistics': {
                'systems': systems_stats,
                'assemblies': assemblies_stats,
                'components': components_stats
            }
        },
        'systems': systems,
        'assemblies': assemblies,
        'components': components
    }
    
    # Save output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "combined_triple_extraction_1_and_2.json"
    
    print(f"\n💾 Saving combined extraction to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("✅ COMBINATION COMPLETE")
    print("=" * 60)
    print(f"\n📊 STATISTICS:")
    print(f"\nSystems:")
    print(f"  Total: {len(systems)}")
    print(f"  Previous: {systems_stats['previous']}, Current: {systems_stats['current']}, Overlap: {systems_stats['overlap']}")
    print(f"  Descriptions combined: {systems_stats['descriptions_combined']}")
    print(f"  Names preserved: {systems_stats['names_preserved']}")
    
    print(f"\nAssemblies:")
    print(f"  Total: {len(assemblies)}")
    print(f"  Previous: {assemblies_stats['previous']}, Current: {assemblies_stats['current']}, Overlap: {assemblies_stats['overlap']}")
    print(f"  Descriptions combined: {assemblies_stats['descriptions_combined']}")
    print(f"  Names preserved: {assemblies_stats['names_preserved']}")
    print(f"  Parent codes preserved: {assemblies_stats['parent_codes_preserved']}")
    
    print(f"\nComponents:")
    print(f"  Total: {len(components)}")
    print(f"  Previous: {components_stats['previous']}, Current: {components_stats['current']}, Overlap: {components_stats['overlap']}")
    print(f"  Descriptions combined: {components_stats['descriptions_combined']}")
    print(f"  Names preserved: {components_stats['names_preserved']}")
    print(f"  Parent codes preserved: {components_stats['parent_codes_preserved']}")
    
    print(f"\nRelationships:")
    print(f"  Total: {total_relationships}")
    print(f"  Assembly→System: {assembly_relationships}")
    print(f"  Component→Assembly: {component_relationships}")
    
    print(f"\n📄 Output saved to: {output_file}")


if __name__ == "__main__":
    main()

