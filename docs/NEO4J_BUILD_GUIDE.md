# Neo4j Database Build Guide

This document describes the process used to build the VMRS Knowledge Graph in Neo4j.

## Final Database State

| Node Type | Count | Description |
|-----------|-------|-------------|
| System | 227 | Top-level VMRS categories (3-digit codes) |
| Assembly | 2,035 | Mid-level groupings (6-digit codes) |
| Component | 35,974 | Specific parts (9-digit codes) |
| VendorPart | 20,339 | Physical parts from vendor inventory |
| Vendor | 517 | Manufacturer/supplier codes |

| Relationship | Count | Description |
|--------------|-------|-------------|
| PART_OF | 38,009 | VMRS hierarchy (Component → Assembly → System) |
| MAPS_TO | 19,966 | Links vendor parts to VMRS components |
| MANUFACTURES | 19,083 | Links vendors to their parts |

### Schema Diagram

```
┌──────────┐     ┌──────────┐     ┌───────────┐
│  System  │ ←── │ Assembly │ ←── │ Component │  (VMRS Hierarchy)
└──────────┘     └──────────┘     └───────────┘
                                        ↑
                                   [:MAPS_TO]
                                        │
                                  ┌───────────┐
                                  │VendorPart │  ( Vendor Part Information)
                                  └───────────┘
                                        ↑
                                 [:MANUFACTURES]
                                        │
                                   ┌────────┐
                                   │ Vendor │
                                   └────────┘
```

---

## Build Process Overview

### Phase 1: VMRS Data Extraction

Extract VMRS codes from source handbook (39 markdown files in `md data/`).

**Tabular extraction** (CSV parsing):
- `scripts/data_processing/extract_vmrs_to_csv.py` → individual CSVs
- `scripts/data_processing/combine_vmrs_csv.py` → `csv data/VMRS_COMPLETE_v20_MASTER.csv`
- `scripts/deduplicate_csv.py` → `csv data/VMRS_COMPLETE_v20_MASTER_deduplicated.csv`

**Non-tabular extraction** (LLM):
- `scripts/run_ingest_from_file.py` → `knowledge_graph_output/combined_triple_extraction_1_and_2.json`
- `scripts/merge_csv_with_json.py` → `knowledge_graph_output/combined_triple_extraction_and_md_tables.json`

### Phase 2: Import VMRS to Neo4j

- `scripts/import_csv_to_neo4j.py`
- Creates System, Assembly, Component nodes with PART_OF relationships

### Phase 3: Vendor Data Import

Source: `vendor data/checked/Motors Part Cleanup - Return Data.csv`

- `scripts/create_vendor_nodes.py` → 517 Vendor nodes
- `scripts/refactor_vendor_schema.py` → 20,339 VendorPart nodes + relationships

### Phase 4: Fix Orphaned VendorParts

- `scripts/fix_orphaned_vendor_parts.py`
- Created 101 missing Component nodes from vendor data
- Linked 721 previously orphaned VendorParts
- Exported 373 unclassified parts to `eda/unclassified_vendor_parts.csv`

---

## Design Decisions

1. **Dual extraction**: CSV parsing for tables + LLM for narrative text
2. **CSV takes precedence**: More accurate for structured data
3. **Separate VendorPart from Component**: Keeps VMRS hierarchy pure
4. **Create missing Components from vendor data**: Ensures all vendor parts can link

---

## How to Rebuild

```bash
# 1. Extract VMRS from markdown → CSV
python3 scripts/data_processing/extract_vmrs_to_csv.py
python3 scripts/data_processing/combine_vmrs_csv.py
python3 scripts/deduplicate_csv.py

# 2. Run LLM triple extraction (non-tabular content)
# Output goes to: knowledge_graph_output/run_YYYYMMDD_HHMMSS/knowledge_graph.json
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md

# 3. Combine LLM extraction runs (if multiple runs)
# Adjust paths to your actual extraction outputs
PYTHONPATH=. python3 scripts/combine_extractions.py \
  --previous knowledge_graph_output/run_YYYYMMDD_HHMMSS/knowledge_graph.json \
  --current knowledge_graph_output/run_YYYYMMDD_HHMMSS/knowledge_graph.json
# Output: knowledge_graph_output/combined_triple_extraction_1_and_2.json

# 4. Merge CSV + LLM extractions
PYTHONPATH=. python3 scripts/merge_csv_with_json.py
# Output: knowledge_graph_output/combined_triple_extraction_and_md_tables.json

# 5. Clear Neo4j database
# In Neo4j Browser: MATCH (n) DETACH DELETE n

# 6. Import VMRS hierarchy from merged JSON
PYTHONPATH=. python3 scripts/neo4j_import.py \
  knowledge_graph_output/combined_triple_extraction_and_md_tables.json

# 7. Import vendor data
python3 scripts/create_vendor_nodes.py
python3 scripts/refactor_vendor_schema.py
python3 scripts/fix_orphaned_vendor_parts.py
```

---

## Key Files

| File | Contents |
|------|----------|
| `csv data/VMRS_COMPLETE_v20_MASTER.csv` | Combined VMRS codes (66,729 rows) |
| `knowledge_graph_output/combined_triple_extraction_and_md_tables.json` | Merged CSV + LLM extractions |
| `vendor data/checked/Motors Part Cleanup - Return Data.csv` | Cleaned vendor data (20,348 parts) |
| `eda/unclassified_vendor_parts.csv` | 373 parts needing VMRS classification: "unable to code" |
