# VMRS Data Processing, Knowledge Graph, and HITL

Toolkit for processing/analyzing VMRS data, building a Neo4j-backed knowledge graph, and capturing human-in-the-loop (HITL) feedback to improve mappings over time.

## 📁 Project Structure

```
vmrs/
├── README.md                          # This file
│
├── scripts/                           # Pipeline scripts (ETL, imports, validation)
│   ├── data_processing/               # CSV extraction + transformation scripts
│   └── import_csv_to_neo4j.py         # Neo4j import entry point (see docs)
│
├── src/                               # Core pipeline modules (chunking, extraction, Neo4j client)
│
├── docs/                              # Canonical docs + analysis reports
│   ├── NEO4J_BUILD_GUIDE.md
│   ├── KNOWLEDGE_GRAPH_GUIDE.md
│   └── analysis/
│
├── csv data/                          # Canonical VMRS tables (CSV exports)
├── md data/                           # VMRS handbook markdown inputs
├── vendor data/                       # Vendor part sources (raw + checked)
├── knowledge_graph_output/            # Graph build outputs (JSON/CSV)
├── tests/test_questions/              # Current QA evidence + scoring + plans
│
├── interface prompts/                 # Claude Desktop prompt variants + HITL guidance
├── mcp/hitl_get_feedback/server.py    # HITL MCP server (feedback capture)
├── HitL_local/                        # HITL design notes + local pending submissions (gitignored)
└── eda/                               # Exploratory analysis artifacts
```

## 📊 Key Datasets

### VMRS Data
- Master hierarchy: `csv data/VMRS_COMPLETE_v20_MASTER.csv` (66,729 codes)
- Handbook source pages: `md data/`

### Vendor Data
- Raw vendor inputs: `vendor data/`
- Checked/ground-truth subset (used by current QA artifacts): `vendor data/checked/Motors Part Cleanup - Return Data.csv`

## 🚀 Quick Start

### Install

```bash
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
cp .env.example .env
```

### 1. Data Processing

```bash
# Convert Excel vendor data to CSV
python3 scripts/data_processing/excel_to_csv.py

# Sort vendor data by each column
python3 scripts/data_processing/sort_vendor_csv.py

# Extract VMRS codes from markdown (if needed)
python3 scripts/data_processing/extract_vmrs_to_csv.py

# Combine and validate (if needed)
python3 scripts/data_processing/combine_vmrs_csv.py
python3 scripts/data_processing/validate_vmrs_csv.py
```

### 2. Build / query Neo4j
See `docs/NEO4J_BUILD_GUIDE.md`.

### 3. Testing (current)
All current testing assets live under `tests/test_questions/`:
- `tests/test_questions/test_log.csv` (questions + expected answers)
- `tests/test_questions/conversations/*.md` (evidence transcripts)
- `tests/test_questions/EVALUATION_SUMMARY.md` (results + gaps)

### 4. HITL feedback capture (MVP)
- MCP server: `mcp/hitl_get_feedback/server.py`
- Prompt guidance: `interface prompts/lookup_agent/hitl_feedback_capture.txt`
- HITL step plan: `dev_plans/hitl_plan.md`
