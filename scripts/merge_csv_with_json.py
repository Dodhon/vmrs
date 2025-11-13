#!/usr/bin/env python3
"""
Merge CSV hierarchy data with existing knowledge graph JSON.

This script:
1. Reads VMRS_COMPLETE_v20_MASTER_deduplicated.csv
2. Extracts systems, assemblies, and components from code_9d
3. Merges with existing knowledge_graph JSON
4. Builds full tree relationships (parent-child links)
5. Outputs combined JSON file with complete hierarchy

WALKTHROUGH:
============
STEP 1: Parse code_9d
  - Input: "174-001-110" (9-digit code)
  - Output: system="174", assembly="174-001", component="174-001-110"

STEP 2: Extract from CSV
  - Read each row with code_9d
  - For each code_9d, create system, assembly, and component entities
  - Track unique entities (no duplicates)

STEP 3: Merge with JSON
  - For each entity type (system/assembly/component):
    - If code exists in BOTH: merge names/descriptions, mark source="both"
    - If code only in JSON: keep as-is, mark source="previous"
    - If code only in CSV: keep as-is, mark source="csv"
  - Preserve alternative names and parent codes when they differ

STEP 4: Build Relationships
  - For each System: find all child assemblies → related_parts.child_assemblies
  - For each Assembly: find parent system + child components → related_parts
  - For each Component: find parent assembly + parent system + siblings → related_parts

STEP 5: Output JSON
  - Create final JSON with metadata, statistics, and all entities
  - Save with timestamp
"""

import csv
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, Set, Tuple


# ============================================================================
# STEP 1: PARSE CODE_9D
# ============================================================================

def parse_code_9d(code_9d: str) -> Tuple[str, str, str]:
    """
    Parse code_9d to extract system, assembly, and component codes.
    
    Example:
      Input:  "174-001-110"
      Output: ("174", "174-001", "174-001-110")
    
    The 9-digit code format is: SYSTEM-ASSEMBLY-COMPONENT
    - System:   First 3 digits (174)
    - Assembly: First 6 digits (174-001)
    - Component: Full 9 digits (174-001-110)
    """
    if not code_9d or not code_9d.strip():
        return (None, None, None)
    
    code_9d = code_9d.strip()
    
    # Validate format: must be exactly XXX-XXX-XXX (3 digits, dash, 3 digits, dash, 3 digits)
    if not re.match(r'^\d{3}-\d{3}-\d{3}$', code_9d):
        return (None, None, None)
    
    # Split by dash and extract parts
    parts = code_9d.split('-')
    system_code = parts[0]                    # "174"
    assembly_code = f"{parts[0]}-{parts[1]}"  # "174-001"
    component_code = code_9d                  # "174-001-110"
    
    return (system_code, assembly_code, component_code)


# ============================================================================
# STEP 2: EXTRACT FROM CSV
# ============================================================================

def extract_from_csv(csv_file: str) -> Dict:
    """
    Extract systems, assemblies, and components from CSV file.
    
    Process:
    1. Read CSV file row by row
    2. For each row with code_9d:
       - Parse to get system, assembly, component codes
       - Create system entity (if not already created)
       - Create assembly entity (if not already created)
       - Create component entity and collect ALL descriptions for same code
    3. Return all unique entities with combined descriptions
    
    Returns:
        Dictionary with 'systems', 'assemblies', 'components' lists
    """
    print(f"📊 Reading CSV: {csv_file}")
    
    # Use dictionaries to track unique entities by code (prevents duplicates)
    systems: Dict[str, Dict] = {}      # code -> entity dict
    assemblies: Dict[str, Dict] = {}  # code -> entity dict
    components: Dict[str, Dict] = {}  # code -> entity dict
    
    # Track all descriptions for each code (using sets to avoid duplicates)
    component_descriptions: Dict[str, Set[str]] = defaultdict(set)
    component_names: Dict[str, Set[str]] = defaultdict(set)
    
    # Read CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"✅ Read {len(rows):,} rows")
    
    skipped = 0
    
    # Process each row
    for i, row in enumerate(rows):
        # Progress indicator every 5000 rows
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1:,}/{len(rows):,} rows...")
        
        # Get code_9d and description from CSV row
        code_9d = row.get('code_9d', '').strip()
        description = row.get('description', '').strip()
        
        # Skip rows without code_9d
        if not code_9d:
            skipped += 1
            continue
        
        # Parse code_9d to get system, assembly, component codes
        system_code, assembly_code, component_code = parse_code_9d(code_9d)
        
        # Skip if parsing failed
        if not system_code:
            skipped += 1
            continue
        
        # Create system entity (only once per system code)
        if system_code not in systems:
            systems[system_code] = {
                'code': system_code,
                'name': f"System {system_code}",  # Generic name, will be merged with JSON if available
                'description': f"VMRS System {system_code}"
            }
        
        # Create assembly entity (only once per assembly code)
        if assembly_code not in assemblies:
            assemblies[assembly_code] = {
                'code': assembly_code,
                'name': f"Assembly {assembly_code}",  # Generic name, will be merged with JSON if available
                'parent_system_code': system_code,    # Link to parent system
                'description': f"VMRS Assembly {assembly_code}"
            }
        
        # Collect all descriptions and names for this component code
        if description:
            component_descriptions[component_code].add(description)
            component_names[component_code].add(description)
        
        # Create component entity structure (will be finalized after collecting all descriptions)
        if component_code not in components:
            components[component_code] = {
                'code': component_code,
                'parent_assembly_code': assembly_code,  # Link to parent assembly
            }
    
    # Finalize components with all collected descriptions
    for component_code, comp in components.items():
        descriptions = component_descriptions.get(component_code, set())
        names = component_names.get(component_code, set())
        
        # Combine all descriptions with " / " separator
        if descriptions:
            combined_desc = " / ".join(sorted(descriptions))  # Sort for consistency
            # Use first description as primary name, or combined if multiple
            if len(names) == 1:
                comp['name'] = list(names)[0]
            else:
                comp['name'] = combined_desc
            comp['description'] = combined_desc
        else:
            comp['name'] = f"Component {component_code}"
            comp['description'] = ""
    
    print(f"✅ Extracted: {len(systems)} systems, {len(assemblies)} assemblies, {len(components)} components")
    print(f"   Skipped: {skipped} rows")
    
    # Return as lists (convert from dicts)
    return {
        'systems': list(systems.values()),
        'assemblies': list(assemblies.values()),
        'components': list(components.values())
    }


# ============================================================================
# STEP 3: MERGE ENTITIES
# ============================================================================

def combine_descriptions(*descriptions: str) -> str:
    """
    Combine multiple descriptions with " / " separator, handling duplicates.
    
    Examples:
      "Fuel System" + "Fuel System" → "Fuel System" (no duplicate)
      "Fuel System" + "Engine Fuel" → "Fuel System / Engine Fuel"
      "Desc 1" + "Desc 2" + "Desc 3" → "Desc 1 / Desc 2 / Desc 3"
      "" + "Fuel System" → "Fuel System"
    """
    # Collect all non-empty, unique descriptions
    unique_descs = set()
    for desc in descriptions:
        desc = desc.strip() if desc else ""
        if desc:
            unique_descs.add(desc)
    
    if not unique_descs:
        return ""
    if len(unique_descs) == 1:
        return list(unique_descs)[0]
    
    # Sort for consistency and join with " / "
    return " / ".join(sorted(unique_descs))


def merge_entities(prev_entities: list, csv_entities: list, entity_type: str) -> Dict:
    """
    Merge entities from JSON (previous) and CSV (current).
    
    Merge Logic:
    1. For each unique code:
       - If exists in BOTH: merge names/descriptions, mark source="both"
       - If only in JSON: keep as-is, mark source="previous"
       - If only in CSV: keep as-is, mark source="csv"
    
    2. When merging:
       - Names: Prefer meaningful names over generic "System XXX"
       - Descriptions: Combine with " | " separator
       - Parent codes: Prefer CSV (more accurate from code_9d parsing)
       - Store alternatives when they differ
    
    Returns:
        Dictionary with:
        - 'entities': list of merged entities
        - 'stats': merge statistics
    """
    # Index entities by code for fast lookup
    prev_by_code = {e['code']: e for e in prev_entities}
    csv_by_code = {e['code']: e for e in csv_entities}
    
    merged = {}
    stats = {
        'previous': len(prev_entities),  # Count from JSON
        'csv': len(csv_entities),        # Count from CSV
        'overlap': 0,                    # Count of codes in both
        'descriptions_combined': 0,      # Count of merged descriptions
        'names_preserved': 0,            # Count of alternative names saved
        'parent_codes_preserved': 0      # Count of alternative parent codes saved
    }
    
    # Get all unique codes from both sources
    all_codes = set(prev_by_code.keys()) | set(csv_by_code.keys())
    
    # Process each code
    for code in all_codes:
        prev_entity = prev_by_code.get(code)  # Entity from JSON
        csv_entity = csv_by_code.get(code)    # Entity from CSV
        
        if prev_entity and csv_entity:
            # ============================================================
            # CASE 1: Code exists in BOTH sources → MERGE
            # ============================================================
            stats['overlap'] += 1
            
            # Determine primary name
            # Strategy: Prefer meaningful names over generic "System XXX" or "Assembly XXX"
            prev_name = prev_entity.get('name', '').strip()
            csv_name = csv_entity.get('name', '').strip()
            
            # If JSON name is generic (starts with "System " or "Assembly "),
            # prefer CSV name if it's more meaningful
            if prev_name.startswith('System ') or prev_name.startswith('Assembly '):
                if csv_name and not csv_name.startswith('System ') and not csv_name.startswith('Assembly '):
                    # CSV has meaningful name, use it
                    primary_name = csv_name
                    alternative_name = prev_name if prev_name != csv_name else None
                else:
                    # Both are generic, use JSON
                    primary_name = prev_name
                    alternative_name = csv_name if csv_name != prev_name else None
            else:
                # JSON has meaningful name, prefer it
                primary_name = prev_name
                alternative_name = csv_name if csv_name != prev_name and csv_name else None
            
            # Combine descriptions
            # CSV description may already contain multiple descriptions joined with " / "
            # Split them and combine with JSON description
            prev_desc = prev_entity.get('description', '')
            csv_desc = csv_entity.get('description', '')
            
            # Split CSV description if it contains " / " separator
            csv_descs = [d.strip() for d in csv_desc.split(' / ')] if csv_desc else []
            # Add JSON description to the list
            all_descs = [prev_desc] if prev_desc else []
            all_descs.extend(csv_descs)
            
            # Combine all descriptions
            combined_desc = combine_descriptions(*all_descs)
            if prev_desc and csv_desc and prev_desc != csv_desc:
                stats['descriptions_combined'] += 1
            
            # Build merged entity
            merged_entity = {
                'code': code,
                'name': primary_name,
                'description': combined_desc,
                'source': 'both'  # Mark as coming from both sources
            }
            
            # Add alternative name if different
            if alternative_name:
                merged_entity['alternative_names'] = [alternative_name]
                stats['names_preserved'] += 1
            
            # Handle parent codes (for assemblies and components only)
            if entity_type == 'assemblies':
                # Assembly → System relationship
                prev_parent = prev_entity.get('parent_system_code', '')
                csv_parent = csv_entity.get('parent_system_code', '')
                
                # Prefer CSV parent (more accurate from code_9d parsing)
                if csv_parent:
                    merged_entity['parent_system_code'] = csv_parent
                    # If JSON had different parent, save as alternative
                    if prev_parent and prev_parent != csv_parent:
                        merged_entity['alternative_parent_system_codes'] = [prev_parent]
                        stats['parent_codes_preserved'] += 1
                elif prev_parent:
                    merged_entity['parent_system_code'] = prev_parent
            
            elif entity_type == 'components':
                # Component → Assembly relationship
                prev_parent = prev_entity.get('parent_assembly_code', '')
                csv_parent = csv_entity.get('parent_assembly_code', '')
                
                # Prefer CSV parent (more accurate from code_9d parsing)
                if csv_parent:
                    merged_entity['parent_assembly_code'] = csv_parent
                    # If JSON had different parent, save as alternative
                    if prev_parent and prev_parent != csv_parent:
                        merged_entity['alternative_parent_assembly_codes'] = [prev_parent]
                        stats['parent_codes_preserved'] += 1
                elif prev_parent:
                    merged_entity['parent_assembly_code'] = prev_parent
            
            merged[code] = merged_entity
            
        elif prev_entity:
            # ============================================================
            # CASE 2: Code only in JSON → Keep as-is
            # ============================================================
            entity = prev_entity.copy()
            entity['source'] = 'previous'
            merged[code] = entity
            
        else:
            # ============================================================
            # CASE 3: Code only in CSV → Keep as-is
            # ============================================================
            entity = csv_entity.copy()
            entity['source'] = 'csv'
            merged[code] = entity
    
    return {
        'entities': list(merged.values()),
        'stats': stats
    }


# ============================================================================
# STEP 4: BUILD RELATIONSHIPS (TREE STRUCTURE)
# ============================================================================

def build_related_parts(systems: list, assemblies: list, components: list) -> Dict:
    """
    Build related_parts tracking for all entities to create full tree structure.
    
    This function creates bidirectional relationships:
    - Systems know their child assemblies
    - Assemblies know their parent system and child components
    - Components know their parent assembly, parent system, and siblings
    
    Process:
    1. Index all entities by code for fast lookup
    2. Build child lists:
       - For each assembly: add to its system's child list
       - For each component: add to its assembly's child list
    3. Add related_parts to each entity:
       - Systems: child_assemblies, total_children
       - Assemblies: parent_system, child_components, total_children
       - Components: parent_assembly, parent_system, sibling_components
    """
    # Index entities by code for fast lookup
    systems_by_code = {s['code']: s for s in systems}
    assemblies_by_code = {a['code']: a for a in assemblies}
    components_by_code = {c['code']: c for c in components}
    
    # Build child relationship maps
    system_children = defaultdict(list)   # system_code -> [assembly_codes]
    assembly_children = defaultdict(list)  # assembly_code -> [component_codes]
    
    # For each assembly, add it to its parent system's child list
    for assembly in assemblies:
        parent_sys = assembly.get('parent_system_code', '')
        if parent_sys and parent_sys in systems_by_code:
            system_children[parent_sys].append(assembly['code'])
    
    # For each component, add it to its parent assembly's child list
    for component in components:
        parent_asm = component.get('parent_assembly_code', '')
        if parent_asm and parent_asm in assemblies_by_code:
            assembly_children[parent_asm].append(component['code'])
    
    # ============================================================
    # Add related_parts to SYSTEMS
    # ============================================================
    for system in systems:
        code = system['code']
        children = system_children.get(code, [])
        system['related_parts'] = {
            'child_assemblies': children,      # List of all assembly codes under this system
            'total_children': len(children)   # Count of child assemblies
        }
    
    # ============================================================
    # Add related_parts to ASSEMBLIES
    # ============================================================
    for assembly in assemblies:
        code = assembly['code']
        parent_sys = assembly.get('parent_system_code', '')
        children = assembly_children.get(code, [])
        
        related = {
            'total_children': len(children)  # Count of child components
        }
        
        # Add parent system reference
        if parent_sys:
            related['parent_system'] = parent_sys
        
        # Add child components list
        if children:
            related['child_components'] = children
        
        assembly['related_parts'] = related
    
    # ============================================================
    # Add related_parts to COMPONENTS
    # ============================================================
    for component in components:
        code = component['code']
        parent_asm = component.get('parent_assembly_code', '')
        
        related = {}
        
        if parent_asm:
            # Add parent assembly reference
            related['parent_assembly'] = parent_asm
            
            # Get parent system from assembly (grandparent)
            if parent_asm in assemblies_by_code:
                parent_sys = assemblies_by_code[parent_asm].get('parent_system_code', '')
                if parent_sys:
                    related['parent_system'] = parent_sys
            
            # Get sibling components (components with same parent assembly)
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


# ============================================================================
# STEP 5: MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point - orchestrates the entire merge process."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Merge CSV hierarchy with knowledge graph JSON')
    parser.add_argument('--csv',
                       default='csv data/VMRS_COMPLETE_v20_MASTER_deduplicated.csv',
                       help='Path to deduplicated VMRS CSV file')
    parser.add_argument('--json',
                       default='knowledge_graph_output/combined_triple_extraction_1_and_2.json',
                       help='Path to existing knowledge graph JSON')
    parser.add_argument('--output-dir',
                       default='knowledge_graph_output',
                       help='Output directory for merged JSON')
    
    args = parser.parse_args()
    
    # ============================================================
    # Load existing JSON
    # ============================================================
    json_path = Path(args.json)
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return
    
    print(f"📥 Loading JSON: {json_path}")
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    # ============================================================
    # Extract from CSV
    # ============================================================
    csv_data = extract_from_csv(args.csv)
    
    # ============================================================
    # Merge entities (systems, assemblies, components)
    # ============================================================
    print("\n🔄 Merging entities...")
    
    # Merge systems
    systems_result = merge_entities(
        json_data.get('systems', []),
        csv_data.get('systems', []),
        'systems'
    )
    systems = systems_result['entities']
    systems_stats = systems_result['stats']
    
    # Merge assemblies
    assemblies_result = merge_entities(
        json_data.get('assemblies', []),
        csv_data.get('assemblies', []),
        'assemblies'
    )
    assemblies = assemblies_result['entities']
    assemblies_stats = assemblies_result['stats']
    
    # Merge components
    components_result = merge_entities(
        json_data.get('components', []),
        csv_data.get('components', []),
        'components'
    )
    components = components_result['entities']
    components_stats = components_result['stats']
    
    # ============================================================
    # Build relationship tree
    # ============================================================
    print("🔗 Building related parts...")
    result = build_related_parts(systems, assemblies, components)
    systems = result['systems']
    assemblies = result['assemblies']
    components = result['components']
    
    # ============================================================
    # Calculate statistics
    # ============================================================
    assembly_relationships = sum(1 for a in assemblies if a.get('parent_system_code'))
    component_relationships = sum(1 for c in components if c.get('parent_assembly_code'))
    total_relationships = assembly_relationships + component_relationships
    
    # ============================================================
    # Build output JSON structure
    # ============================================================
    output_data = {
        'metadata': {
            'total_systems': len(systems),
            'total_assemblies': len(assemblies),
            'total_components': len(components),
            'total_relationships': total_relationships,
            'extraction_date': datetime.now().isoformat(),
            'sources': {
                'json': str(json_path),
                'csv': args.csv
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
    
    # ============================================================
    # Save output file
    # ============================================================
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "combined_triple_extraction_and_md_tables.json"
    
    print(f"\n💾 Saving merged JSON to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # ============================================================
    # Print summary statistics
    # ============================================================
    print("\n" + "=" * 60)
    print("✅ MERGE COMPLETE")
    print("=" * 60)
    print(f"\n📊 STATISTICS:")
    print(f"\nSystems:")
    print(f"  Total: {len(systems)}")
    print(f"  JSON: {systems_stats['previous']}, CSV: {systems_stats['csv']}, Overlap: {systems_stats['overlap']}")
    print(f"  Descriptions combined: {systems_stats['descriptions_combined']}")
    print(f"  Names preserved: {systems_stats['names_preserved']}")
    
    print(f"\nAssemblies:")
    print(f"  Total: {len(assemblies)}")
    print(f"  JSON: {assemblies_stats['previous']}, CSV: {assemblies_stats['csv']}, Overlap: {assemblies_stats['overlap']}")
    print(f"  Descriptions combined: {assemblies_stats['descriptions_combined']}")
    print(f"  Names preserved: {assemblies_stats['names_preserved']}")
    print(f"  Parent codes preserved: {assemblies_stats['parent_codes_preserved']}")
    
    print(f"\nComponents:")
    print(f"  Total: {len(components)}")
    print(f"  JSON: {components_stats['previous']}, CSV: {components_stats['csv']}, Overlap: {components_stats['overlap']}")
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
