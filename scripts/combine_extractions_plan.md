# Plan: Combine Previous and Current Triple Extraction Runs

## Overview
Create a script to merge the previous and current triple extraction runs into a single combined knowledge graph.

## Files to Create

### 1. `scripts/combine_extractions.py`
Main script to combine extraction runs.

## Input Files
- **Previous run**: `knowledge_graph_output/archive_20251111_194648/knowledge_graph_20251111_175715.json`
- **Current run**: `knowledge_graph_output/run_20251111_194658/knowledge_graph_20251111_195654.json`

## Output
- **Combined JSON**: `knowledge_graph_output/combined_extraction_YYYYMMDD_HHMMSS.json`
- **Statistics report**: Console output with merge statistics

## Merge Strategy

### Systems
- Merge by code (deduplicate)
- If same code exists in both: 
  - Combine descriptions (concatenate with separator if both have descriptions)
  - **Preserve both names**: Use longer name as primary, store alternative in `alternative_names` array
  - Track source (previous/current/both)
- Track related parts: systems that share relationships
- **No information lost**: All names, descriptions, and codes preserved

### Assemblies
- Merge by code (deduplicate)
- If same code exists in both:
  - Combine descriptions (concatenate with separator if both have descriptions)
  - **Preserve both names**: Use longer name as primary, store alternative in `alternative_names` array
  - **Preserve both parent codes**: Use current as primary `parent_system_code`, store previous in `alternative_parent_system_codes` if different
  - Track source (previous/current/both)
- Track related parts: parent system, child components
- **No information lost**: All names, descriptions, parent codes, and relationships preserved

### Components
- Merge by code (deduplicate)
- If same code exists in both:
  - Combine descriptions (concatenate with separator if both have descriptions)
  - **Preserve both names**: Use longer name as primary, store alternative in `alternative_names` array
  - **Preserve both parent codes**: Use current as primary `parent_assembly_code`, store previous in `alternative_parent_assembly_codes` if different
  - Track source (previous/current/both)
- Track related parts: parent assembly, sibling components
- **No information lost**: All names, descriptions, parent codes, and relationships preserved

## Deduplication Rules
1. **Same code in both**: 
   - **Descriptions**: Combine with " | " separator if both have descriptions
   - If only one has description, use that one
   - If descriptions are identical, keep single copy (no duplication)
   - **Names**: Use longer name as primary, store alternative name(s) in `alternative_names` array if different
   - If names are identical, keep single copy
   - **Parent codes**: Use current as primary, store alternative in `alternative_parent_*_codes` array if different
2. **Code format**: Normalize to ensure consistent format (e.g., "001" not "1")
3. **Relationships**: Auto-calculate from parent codes after merge
4. **Related parts tracking**: 
   - For each entity, track related entities (parent, children, siblings)
   - Build relationship graph after merge
5. **Information preservation**: 
   - All unique codes preserved (no entities lost)
   - All descriptions preserved (combined if duplicate code)
   - All names preserved (primary + alternatives)
   - All parent relationships preserved (primary + alternatives)

## Statistics to Report
- Total systems: X (previous: Y, current: Z, overlap: W, descriptions combined: N)
- Total assemblies: X (previous: Y, current: Z, overlap: W, descriptions combined: N)
- Total components: X (previous: Y, current: Z, overlap: W, descriptions combined: N)
- Total relationships: X
- Duplicates resolved: X
- Related parts tracked: X systems, Y assemblies, Z components

## Script Features
- Command-line arguments for input file paths (optional, with defaults)
- Validation of input files
- Progress logging
- Error handling
- Optional: Add metadata field tracking source of each entity

## Usage
```bash
# Default (uses known file paths)
PYTHONPATH=. python3 scripts/combine_extractions.py

# Custom paths
PYTHONPATH=. python3 scripts/combine_extractions.py \
  --previous archive_20251111_194648/knowledge_graph_20251111_175715.json \
  --current run_20251111_194658/knowledge_graph_20251111_195654.json \
  --output combined_extraction.json
```

## Output Format
Same structure as input files with additional fields:
```json
{
  "metadata": {
    "total_systems": X,
    "total_assemblies": Y,
    "total_components": Z,
    "extraction_date": "ISO timestamp",
    "sources": {
      "previous": "file_path",
      "current": "file_path"
    },
    "merge_statistics": {
      "systems": {"previous": X, "current": Y, "overlap": Z, "descriptions_combined": N},
      "assemblies": {...},
      "components": {...}
    }
  },
  "systems": [
    {
      "code": "001",
      "name": "primary name (longer or current)",
      "alternative_names": ["alternative name if different"],
      "description": "combined description if merged",
      "source": "both|previous|current",
      "related_parts": {
        "child_assemblies": ["001-001", "001-002"],
        "total_children": 5
      }
    }
  ],
  "assemblies": [
    {
      "code": "001-001",
      "name": "primary name (longer or current)",
      "alternative_names": ["alternative name if different"],
      "description": "combined description if merged",
      "parent_system_code": "001",
      "alternative_parent_system_codes": ["alternative parent if different"],
      "source": "both|previous|current",
      "related_parts": {
        "parent_system": "001",
        "child_components": ["001-001-001", "001-001-002"],
        "total_children": 3
      }
    }
  ],
  "components": [
    {
      "code": "001-001-001",
      "name": "primary name (longer or current)",
      "alternative_names": ["alternative name if different"],
      "description": "combined description if merged",
      "parent_assembly_code": "001-001",
      "alternative_parent_assembly_codes": ["alternative parent if different"],
      "source": "both|previous|current",
      "related_parts": {
        "parent_assembly": "001-001",
        "parent_system": "001",
        "sibling_components": ["001-001-002"]
      }
    }
  ]
}
```

## Considerations
- Handle missing parent relationships (e.g., assembly references system that doesn't exist)
- Validate code formats before merging
- Preserve all valid entities even if parent is missing
- Log warnings for orphaned entities
- Description combination:
  - Use " | " as separator for combined descriptions
  - Remove duplicate descriptions if identical
  - Preserve order: previous description first, then current
- Name preservation:
  - Store primary name (longer, or current if equal length)
  - Store alternative name(s) in `alternative_names` array if different
  - Only include `alternative_names` field if alternatives exist
- Parent code preservation:
  - Store primary parent code (current if both exist, or whichever exists)
  - Store alternative parent code(s) in `alternative_parent_*_codes` array if different
  - Only include alternative parent fields if alternatives exist
- Related parts tracking:
  - Build relationship graph after all entities are merged
  - For systems: track all child assemblies
  - For assemblies: track parent system and all child components
  - For components: track parent assembly, parent system, and sibling components
  - Only include valid relationships (parent exists)
- **Information preservation guarantee**:
  - All entities preserved (no codes lost)
  - All descriptions preserved (combined if duplicate)
  - All names preserved (primary + alternatives)
  - All parent relationships preserved (primary + alternatives)

