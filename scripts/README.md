# VMRS Scripts

Python scripts for processing and analyzing VMRS and vendor parts data.

## 📂 Data Processing Scripts (`data_processing/`)

### 1. `extract_vmrs_to_csv.py`
**Purpose**: Extract VMRS codes from markdown files and convert to CSV

**Input**: 
- `md data/*.md` - VMRS handbook pages in markdown format

**Output**:
- Individual CSV files for each markdown source
- Extracts code_9d, code_6d, system, subcode, description

**Usage**:
```bash
python3 scripts/data_processing/extract_vmrs_to_csv.py
```

---

### 2. `combine_vmrs_csv.py`
**Purpose**: Combine multiple VMRS CSV files into master dataset

**Input**:
- `csv data/VMRS_HB_COMPLETE_v20 page *_pages_*.csv` - Individual CSV files

**Output**:
- `csv data/VMRS_COMPLETE_v20_MASTER.csv` - Master dataset (66,729 codes)
- `csv data/master_summary.json` - Summary statistics

**Usage**:
```bash
python3 scripts/data_processing/combine_vmrs_csv.py
```

---

### 3. `validate_vmrs_csv.py`
**Purpose**: Validate VMRS data quality and structure

**Input**:
- `csv data/VMRS_COMPLETE_v20_MASTER.csv`

**Output**:
- `csv data/validation_report.json` - Detailed validation results
- `csv data/validation_summary.json` - Summary of issues found

**Checks**:
- Code format consistency
- Hierarchical integrity
- Missing descriptions
- Duplicate codes

**Usage**:
```bash
python3 scripts/data_processing/validate_vmrs_csv.py
```

---

### 4. `sort_master_csv.py`
**Purpose**: Sort VMRS master data by different fields

**Input**:
- `csv data/VMRS_COMPLETE_v20_MASTER.csv`

**Output** (in `eda/`):
- `VMRS_MASTER_sorted_by_code_6d.csv`
- `VMRS_MASTER_sorted_by_code_9d.csv`
- `VMRS_MASTER_sorted_by_system.csv`
- `VMRS_MASTER_sorted_by_subcode.csv`
- `VMRS_MASTER_sorted_by_description.csv`

**Usage**:
```bash
python3 scripts/data_processing/sort_master_csv.py
```

---

### 5. `excel_to_csv.py`
**Purpose**: Convert vendor Excel file to CSV format

**Input**:
- `vendor data/Master Parts list for Richard 06.25.25 (1).xlsx`

**Output**:
- `vendor data/Master Parts list for Richard 06.25.25 (1).csv` (29,710 parts)

**Usage**:
```bash
python3 scripts/data_processing/excel_to_csv.py
```

---

### 6. `sort_vendor_csv.py`
**Purpose**: Create sorted CSV files for each vendor data column

**Input**:
- `vendor data/Master Parts list for Richard 06.25.25 (1).csv`

**Output** (in `vendor data/`):
- `Master_Parts_sorted_by_PART.csv`
- `Master_Parts_sorted_by_MANUFACTURER.csv`
- `Master_Parts_sorted_by_DESCRIPTION.csv`
- `Master_Parts_sorted_by_CLASS.csv`
- `Master_Parts_sorted_by_SYSTEM.csv`
- `Master_Parts_sorted_by_COMPONENT.csv`
- `Master_Parts_sorted_by_ASSEMBLY.csv`
- `Master_Parts_sorted_by_ACTIVE.csv`
- `Master_Parts_sorted_by_COMPLETE_VMRS.csv`
- `Master_Parts_sorted_by_COMPLETE_CLASS.csv`

**Usage**:
```bash
python3 scripts/data_processing/sort_vendor_csv.py
```

---

## 🔄 Typical Workflow

### Initial Setup (First Time)
```bash
# 1. Extract VMRS from markdown
python3 scripts/data_processing/extract_vmrs_to_csv.py

# 2. Combine into master dataset
python3 scripts/data_processing/combine_vmrs_csv.py

# 3. Validate data quality
python3 scripts/data_processing/validate_vmrs_csv.py

# 4. Convert vendor Excel to CSV
python3 scripts/data_processing/excel_to_csv.py

# 5. Create sorted versions
python3 scripts/data_processing/sort_master_csv.py
python3 scripts/data_processing/sort_vendor_csv.py
```

---

## 📊 Output Summary

| Script | Output Files | Key Metric |
|--------|--------------|------------|
| extract_vmrs_to_csv.py | 36+ CSVs | 66,729 codes |
| combine_vmrs_csv.py | 1 master CSV | 100% consolidation |
| validate_vmrs_csv.py | 2 JSON reports | 4.9% empty descriptions |
| sort_master_csv.py | 5 sorted CSVs | - |
| excel_to_csv.py | 1 vendor CSV | 29,710 parts |
| sort_vendor_csv.py | 10 sorted CSVs | - |

---

## 🛠️ Dependencies

All scripts require:
```bash
pip3 install pandas openpyxl
```

---

## 💡 Tips

1. **Run scripts from project root**: All paths are relative to `/vrms/`
2. **Check output directories**: Results go to `csv data/`, `eda/`, or `vendor data/`
3. **Review console output**: Scripts provide detailed progress and statistics
4. **Incremental processing**: Most scripts can be re-run safely (they overwrite)

---

## 🕸️ Knowledge Graph Extraction Scripts

### 1. `run_ingest_from_file.py`
**Purpose**: Extract structured knowledge from VMRS manuals and build a Neo4j knowledge graph

**Input**:
- Any text file (e.g., `llm_matching/matching_context.md`)
- VMRS documentation in text or markdown format

**Output**:
- `e80_eec_knowledge_graph.json` - Complete extraction in JSON format
- `progress_chunk_N.json` - Progress checkpoints for resumption
- Neo4j graph database (if configured)

**What It Extracts**:
- **Systems** (Code Key 31): 3-digit codes (e.g., "044 - Fuel System")
- **Assemblies** (Code Key 32): 6-digit codes (e.g., "044-001 - Fuel Injection")
- **Components** (Code Key 33): 9-digit codes (e.g., "044-001-015 - Fuel Injector")
- **Relationships**: PART_OF hierarchy (Component→Assembly→System)

**Usage**:
```bash
# Basic usage (JSON export only)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md

# With Neo4j (configure .env first)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md

# Resume from checkpoint
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md \
  --start-chunk 50

# Save progress less frequently (faster)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md \
  --save-every 10
```

**Configuration** (`.env` file):
```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (for Neo4j storage)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

**Features**:
- ✅ LLM-based structured extraction (Claude Sonnet 4.5 - latest, most cost-effective)
- ✅ Automatic chunking for large files
- ✅ Code validation (format and range checking)
- ✅ Deduplication by code
- ✅ Progress checkpoints for resumption
- ✅ Dual output (Neo4j + JSON)
- ✅ Handles 800K+ token files

---

### 2. `run_graph_extraction.py`
**Purpose**: Same as `run_ingest_from_file.py` but originally designed for E80 manual

**Input**:
- `data/input/E80_manual_text.txt` (default)
- Any VMRS documentation

**Output**:
- Same as `run_ingest_from_file.py`

**Usage**:
```bash
# Same interface as run_ingest_from_file.py
PYTHONPATH=. python3 scripts/run_graph_extraction.py \
  --start-chunk 0 \
  --save-every 1
```

**Note**: Both scripts use the same underlying `src/graph_builder.py` module.

---

## 🏗️ Core Modules (`src/`)

The graph extraction scripts use these core modules:

### `src/text_chunker.py`
- Splits large documents into ~3000 token chunks
- Preserves paragraph boundaries
- Maintains context with overlap
- Extracts VMRS codes from text

### `src/triple_extractor.py`
- LLM-based structured extraction using Claude Sonnet 4.5
- Strict JSON schema for reliability
- Validates codes (format and range)
- Temperature=0 for deterministic results

### `src/neo4j_client.py`
- Creates and manages Neo4j nodes
- Handles PART_OF relationships
- Automatic deduplication via MERGE
- Creates indexes for performance

### `src/graph_builder.py`
- Orchestrates chunker → extractor → Neo4j flow
- Tracks progress and statistics
- Saves checkpoints
- Exports to JSON and Neo4j

---

## 📊 Knowledge Graph Statistics (Expected)

Processing `llm_matching/matching_context.md` (~810K tokens):

| Metric | Expected Value |
|--------|----------------|
| Total Chunks | ~270 |
| Systems | ~150 |
| Assemblies | ~850 |
| Components | ~4,200 |
| Relationships | ~5,050 |
| Processing Time | 30-60 minutes |

---

## 🔍 Querying the Knowledge Graph

### Neo4j Cypher Queries

```cypher
// Count entities
MATCH (s:System) RETURN count(s) as systems
MATCH (a:Assembly) RETURN count(a) as assemblies
MATCH (c:Component) RETURN count(c) as components

// Find all assemblies in Fuel System
MATCH (a:Assembly)-[:PART_OF]->(s:System {code: "044"})
RETURN a.code, a.name

// Get full hierarchy for a component
MATCH path = (c:Component {code: "044-001-015"})-[:PART_OF*]->(s:System)
RETURN path
```

### Python API

```python
from src.neo4j_client import Neo4jClient
import os
from dotenv import load_dotenv

load_dotenv()
client = Neo4jClient(
    uri=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

stats = client.get_statistics()
print(f"Systems: {stats['systems']}")
client.close()
```

---

## 🔄 Updated Typical Workflow

### Phase 1: Data Processing (Existing)
```bash
# 1-7. Same as before
python3 scripts/data_processing/extract_vmrs_to_csv.py
python3 scripts/data_processing/combine_vmrs_csv.py
# ... etc
```

### Phase 2: Knowledge Graph Building (New!)
```bash
# 8. Configure .env
echo "ANTHROPIC_API_KEY=your_key" > .env
echo "NEO4J_URI=bolt://localhost:7687" >> .env
echo "NEO4J_USERNAME=neo4j" >> .env
echo "NEO4J_PASSWORD=password" >> .env

# 9. Install dependencies
pip3 install -r requirements.txt

# 10. Extract knowledge graph
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md

# 11. Query the graph (Neo4j Browser or Python)
# Open http://localhost:7474
```

---

## 📚 Additional Documentation

For detailed setup and usage of knowledge graph extraction:
- **[SETUP_GUIDE.md](../SETUP_GUIDE.md)** - Complete setup instructions
- **[IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)** - Technical details and design

---

## 🛠️ Updated Dependencies

```bash
# Data processing (existing)
pip3 install pandas openpyxl

# Knowledge graph extraction (new)
pip3 install anthropic neo4j python-dotenv
```

Or install everything:
```bash
pip3 install -r requirements.txt
```

---

*Last Updated: November 11, 2025*
