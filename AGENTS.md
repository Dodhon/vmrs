# Copy of CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. All edits to this file must also be applied to CLAUDE.md

## Project Overview

VMRS Data Processing & Analysis - A comprehensive toolkit for processing, analyzing, and linking Vehicle Maintenance Reporting Standards (VMRS) data with vendor parts data. The project combines traditional data processing (CSV extraction/validation) with LLM-powered knowledge graph extraction and Neo4j graph database storage.

End goal: the Neo4j graph serves as the backend for a stakeholder-facing chatbot that answers questions about VMRS systems (and their assemblies/components) and related vendor parts.

## Key Datasets

### VMRS Data (66,729 codes)
- **Structure**: 3-level hierarchy: System (XXX) → Assembly (XXX) → Component (XXX)
- **9-digit codes**: `XXX-XXX-XXX` (89.4% - component-level)
- **6-digit codes**: `XXX-XXX` (10.6% - assembly-level)
- **289 systems** with deep component-level detail

**Data Sources (dual extraction):**
- **Tabular**: CSV tables parsed from markdown handbook files → `csv data/VMRS_COMPLETE_v20_MASTER.csv`
- **Non-tabular**: LLM extraction from unstructured text → `knowledge_graph_output/combined_triple_extraction_1_and_2.json`
- **Combined**: Merged via `merge_csv_with_json.py` → `knowledge_graph_output/combined_triple_extraction_and_md_tables.json`

### Vendor Data
- **Original dataset**: `vendor data/Master Parts list for Richard 06.25.25 (1).csv` (29,710 parts)
- **Cleaned dataset**: `vendor data/checked/Motors Part Cleanup - Return Data.csv` (20,348 parts)
- **20,339 VendorPart nodes** in Neo4j with properties: part, description, manf_partmfr, manf_partmfr_name, manf_partnumber, vmrs, system, assembly, component
- **19,245 MAPS_TO relationships** linking VendorPart → Component
- **19,083 MANUFACTURES relationships** linking Vendor → VendorPart
- **517 unique Vendor nodes**

### Code Structure Mapping
```
Vendor: SYSTEM (XXX) - COMPONENT (XXX) - ASSEMBLY (XXX)
   ↓  (reordered to match VMRS)
VMRS:   SYSTEM (XXX) - ASSEMBLY (XXX) - COMPONENT (XXX)
```

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip3 install -r requirements.txt
```

### Data Processing Pipeline (Traditional CSV)
```bash
# 1. Extract VMRS codes from markdown to CSV
python3 scripts/data_processing/extract_vmrs_to_csv.py

# 2. Combine individual CSVs into master dataset
python3 scripts/data_processing/combine_vmrs_csv.py

# 3. Validate data quality
python3 scripts/data_processing/validate_vmrs_csv.py

# 4. Convert vendor Excel to CSV
python3 scripts/data_processing/excel_to_csv.py

# 5. Create sorted versions for analysis
python3 scripts/data_processing/sort_master_csv.py
python3 scripts/data_processing/sort_vendor_csv.py
```

### Knowledge Graph Extraction (LLM-powered, non-tabular)
```bash
# Extract knowledge graph from VMRS documentation
# Requires: ANTHROPIC_API_KEY in .env
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md

# With Neo4j storage (requires Neo4j credentials in .env)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md \
  --save-every 10

# Resume from checkpoint (if interrupted)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md \
  --start-chunk 50
```

### Combine Tabular + Non-Tabular Extractions
```bash
# Merge LLM extraction (non-tabular) with CSV tables (tabular)
PYTHONPATH=. python3 scripts/merge_csv_with_json.py

# This combines:
#   - knowledge_graph_output/combined_triple_extraction_1_and_2.json (LLM)
#   - csv data/VMRS_COMPLETE_v20_MASTER_deduplicated.csv (tables)
# Output: knowledge_graph_output/combined_triple_extraction_and_md_tables.json
```

### Neo4j Import (Direct CSV Import)
```bash
# Import VMRS master CSV directly to Neo4j (faster than LLM extraction)
# Requires: Neo4j credentials in .env
PYTHONPATH=. python3 scripts/import_csv_to_neo4j.py
```

### Testing
```bash
# Run Neo4j acceptance tests
cd tests/neo4j_acceptance
python3 process_questions.py
```

## Architecture & Code Structure

### Core Modules (`src/`)

**`src/text_chunker.py`**
- Splits large documents into ~2000-3000 token chunks
- Preserves paragraph boundaries with ~200 token overlap
- Extracts VMRS codes from text using regex

**`src/triple_extractor.py`**
- LLM-based structured extraction using Claude Sonnet 4.5
- Strict JSON schema for reliability (`temperature=0`)
- Validates VMRS code formats and ranges
- Returns Systems, Assemblies, Components with relationships

**`src/neo4j_client.py`**
- Creates and manages Neo4j graph nodes (System, Assembly, Component)
- Creates PART_OF relationships following VMRS hierarchy
- Automatic deduplication via MERGE
- Creates indexes for performance

**`src/graph_builder.py`**
- Orchestrates: chunker → extractor → Neo4j pipeline
- Progress tracking with checkpoint saves
- Exports to both JSON and Neo4j
- Handles resumption from failed runs

### Main Scripts (`scripts/`)

**Data Processing** (`scripts/data_processing/`)
- CSV extraction, combination, validation, sorting
- See scripts/data_processing/README.md for detailed docs

**Knowledge Graph Extraction**
- `run_ingest_from_file.py` - LLM-based extraction from non-tabular text
- `run_graph_extraction.py` - Same as above (legacy name)
- `combine_extractions.py` - Merge multiple LLM extraction runs
- `merge_csv_with_json.py` - Merge tabular (CSV) + non-tabular (LLM) data
- `import_csv_to_neo4j.py` - Direct CSV import to Neo4j (faster, more accurate)

**Vendor & Enrichment**
- `create_vendor_nodes.py` - Import Vendor nodes to Neo4j
- `refactor_vendor_schema.py` - Create VendorPart nodes and link to Components/Vendors
- `fix_orphaned_vendor_parts.py` - Create missing Components and link orphaned VendorParts
- `check_missing_codes.py` - Verify if specific VMRS codes exist in Neo4j
- `enrich_vmrs_with_vendor_data.py` - Link vendor parts to VMRS codes (legacy)
- `fix_vendor_names.py` - Clean vendor data

### VMRS Hierarchy Pattern

All code must respect the strict 3-level hierarchy:
```
System (e.g., "044 - Fuel System")
  └─> Assembly (e.g., "044-001 - Fuel Injection")
       └─> Component (e.g., "044-001-015 - Fuel Injector")
```

**Code Format Rules:**
- System codes: 3 digits (000-999)
- Assembly codes: 6 digits with hyphen (XXX-XXX)
- Component codes: 9 digits with hyphens (XXX-XXX-XXX)
- First segment ALWAYS matches `system` column
- Second segment ALWAYS matches `subcode` column
- 100% hierarchical integrity (no orphaned codes)

### Neo4j Graph Schema

**Node Types:**
- `System`: 3-digit codes (e.g., "044") - 227 nodes
- `Assembly`: 6-digit codes (e.g., "044-001") - 2,035 nodes
- `Component`: 9-digit codes (e.g., "044-001-015") - 35,974 nodes (35,873 from VMRS + 101 from vendor data)
- `VendorPart`: Physical parts from vendors - 20,339 nodes
- `Vendor`: Manufacturer codes (e.g., "FORDX") - 517 nodes

**Relationships:**
- `PART_OF`: Component → Assembly → System (VMRS hierarchy) - 38,009 relationships
- `MAPS_TO`: VendorPart → Component (links vendor parts to VMRS codes) - 19,966 relationships
- `MANUFACTURES`: Vendor → VendorPart (vendor linkage) - 19,083 relationships

**Schema Diagram:**
```
System ← Assembly ← Component (pure VMRS)
                        ↑
                    [:MAPS_TO]
                        |
                   VendorPart
                        ↑
                 [:MANUFACTURES]
                        |
                     Vendor
```


## Configuration

### Environment Variables (`.env`)
```bash
# Required for LLM extraction
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (for Neo4j storage)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

Copy `.env.example` to `.env` and fill in credentials.

## Data Quality Considerations

### Known Issues
1. **Empty descriptions**: 3,254 records (4.9%) have empty descriptions
2. **OCR errors**: "Dus" → "Bus", "Salety" → "Safety", "Lett" → "Left", etc.
3. **Vendor code ordering**: Vendor codes are System-Component-Assembly (not System-Assembly-Component)
4. **Unclassified vendor parts**: 373 VendorParts have no VMRS code (vmrs='nan') - exported to `eda/unclassified_vendor_parts.csv`

### Code Validation
- All scripts validate VMRS code formats (XXX-XXX-XXX pattern)
- Hierarchical integrity checks ensure parent codes exist
- Some vendor VMRS codes don't exist in VMRS handbook - these Components are created from vendor data (101 total)

## Important Path Conventions

- **Run scripts from project root**: All paths are relative to `/vmrs/`
- **Notes**: `.claude/notes/` is a symlink to `~/.claude/notes/` (daily work notes)
- **Data directories**:
  - `csv data/` - Processed VMRS CSV files
  - `md data/` - Source markdown files (39 VMRS handbook pages)
  - `vendor data/` - Vendor Excel/CSV files (original)
  - `vendor data/checked/` - Cleaned vendor data used for Neo4j import (20,349 parts)
  - `eda/` - Exploratory data analysis outputs
  - `knowledge_graph_output/` - LLM extraction results (timestamped folders)
- **PYTHONPATH**: Set to `.` when running graph extraction scripts

## Testing & Validation

### Neo4j Acceptance Tests
Located in `tests/neo4j_acceptance/`:
- `queries.json` - Test queries with expected answers
- `questions.json` - 50 Q&A test cases
- `process_questions.py` - Test runner
- `qa_results.csv` - Test results

### Stress Tests
Located in `tests/stress_test/`:
- `curated_edge_cases.csv` - 224 curated edge case questions across 9 categories
- `manual_test_results.csv` - Testing spreadsheet with columns for recording actual results
- `edge_cases_summary.md` - Category breakdown and testing procedure
- `v2_chatbot_simulation_results.md` - Pass criteria and expected chatbot behavior

Categories: Data Quality, Ambiguity, Missing Data, Query Complexity, Natural Language, Boundary, Manufacturer, Vendor Query, Not In Database

### Stress Test MCP Server
Located in `mcp/stress_test_mcp.py` - Provides Claude Desktop with read/write access to the testing spreadsheet.

**Tools:**
- `get_next_test()` - Get next untested question
- `get_test_by_id(test_id)` - Get specific test case
- `record_result(test_id, actual_response, pass_fail, notes)` - Record test result
- `get_test_stats()` - Get pass/fail statistics
- `list_tests(category, status, limit)` - List tests with filtering
- `get_categories()` - List all test categories

**Claude Desktop Config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
"stress-test": {
  "command": "/usr/local/bin/python3",
  "args": ["/path/to/vmrs/mcp/stress_test_mcp.py"]
}
```

**Usage in Claude Desktop:**
```
Run all stress tests automatically:
1. get_next_test() from stress-test MCP
2. Query neo4j-aura to answer the question
3. Compare result to expected_vmrs
4. record_result() with PASS/FAIL/PARTIAL
5. Repeat until all 224 tests complete
6. Show final get_test_stats()
```

### Data Validation
- `scripts/data_processing/validate_vmrs_csv.py` generates validation reports
- Check `csv data/validation_report.json` for detailed issues
- Review `csv data/validation_summary.json` for summary stats

## Documentation

- **README.md** - Project overview and quick start
- **scripts/README.md** - Detailed script documentation
- **docs/NEO4J_BUILD_GUIDE.md** - Complete Neo4j database build process and design decisions
- **docs/analysis/PATTERNS_ANALYSIS.md** - VMRS data patterns and insights (9 key insights)
- **docs/analysis/LINKING_PATTERNS.md** - VMRS-vendor linking strategies (5 patterns)
- **docs/analysis/POC_READY_SUBSETS.md** - PoC datasets documentation

## VP Presentation (Dec 2025)

**File:** `VMRS Chatbot (2).pdf` (13 slides)

**Slide Structure:**
1. Title - VMRS Chatbot Dec 2025
2. The Problem - VMRS background, 30k parts, manual lookup challenges
3. Demo - "grille" (works) and "flux capacitor" (graceful failure)
4. Savings and Cost - $160k savings example, $75k labor cost, $20k data cleanup
5. Current Problem vs New Solution - before/after flow diagram
6. The Approach - knowledge graph ingestion with Neo4j
7. Results and Limitations - confident on system/assembly, component needs feedback
8. Tech Stack - Neo4j + Claude (both interchangeable)
9. Next Steps - pilot rollout, learn from operators, Snowflake access
10-13. Appendix - Savings details, development process, handbook link

**Key Talking Points:**
- $160k saved from 240-part filter optimization → extrapolate to 19,000 parts
- Current labor: 5,000 parts × 0.5 hrs × $30/hr = $75k/year
- Data cleanup outsourcing: $20k one-time + $5k annual
- Knowledge graph enables vendor comparison via VMRS code standardization
- Tech stack is vendor-agnostic (Neo4j/Claude can be swapped)

## Git Commit Guidelines

- **Do NOT include** "Generated with Claude Code" or similar AI attribution in commit messages
- **Do NOT include** "Co-Authored-By: Claude" or similar in commit messages
- Keep commit messages concise and focused on what changed

## Common Workflows

### 1. Adding New Vendor Data
```bash
# 1. Place Excel file in vendor data/
# 2. Convert to CSV
python3 scripts/data_processing/excel_to_csv.py
# 3. Fix vendor names if needed
python3 scripts/fix_vendor_names.py
# 4. Import Vendor nodes to Neo4j
python3 scripts/create_vendor_nodes.py
# 5. Create VendorPart nodes and relationships
python3 scripts/refactor_vendor_schema.py
# 6. Fix orphaned VendorParts (creates missing Components)
python3 scripts/fix_orphaned_vendor_parts.py
```

### 2. Rebuilding Knowledge Graph
```bash
# Option A: CSV import (fast, accurate)
PYTHONPATH=. python3 scripts/import_csv_to_neo4j.py

# Option B: LLM extraction (flexible, handles unstructured docs)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md
```

### 3. Analyzing Data Quality
```bash
# Run validation
python3 scripts/data_processing/validate_vmrs_csv.py

# Review reports
cat csv\ data/validation_summary.json
```
