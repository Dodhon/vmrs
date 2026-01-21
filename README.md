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
├── mcp/hitl/server.py                 # HITL MCP server (feedback capture)
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
- MCP server: `mcp/hitl/server.py`
- Prompt guidance: `interface prompts/hitl_feedback_capture.txt`
- HITL step plan: `dev_plans/hitl_plan.md`


## 📖 Documentation

### Analysis Reports

1. **[PATTERNS_ANALYSIS.md](docs/analysis/PATTERNS_ANALYSIS.md)**
   - VMRS code structure and hierarchy
   - System distribution and statistics
   - Data quality issues
   - 9 key insights

2. **[LINKING_PATTERNS.md](docs/analysis/LINKING_PATTERNS.md)**
   - 5 linking patterns identified
   - 93.7% match rate explanation
   - Knowledge graph design
   - Recommended strategies

3. **[POC_READY_SUBSETS.md](docs/analysis/POC_READY_SUBSETS.md)**
   - System 044 PoC (639 parts, 55.6% HIGH quality)
   - Perfect alignment subset (111 parts)
   - Success metrics and recommendations

## 🎯 PoC-Ready Datasets

### Option 1: System 044 (Fuel System) - RECOMMENDED
- **File**: `eda/poc_dataset.csv`
- **Parts**: 639 total, 355 HIGH quality (>0.30 similarity)
- **Use Case**: Focused depth in single system
- **Perfect matches**: Multiple parts with 1.00 similarity

### Option 2: Perfect Alignment (Cross-System)
- **File**: `eda/perfect_alignment_poc.csv`
- **Parts**: 111 with >0.40 similarity
- **Use Case**: Demonstrate breadth across systems
- **Systems**: Multiple (013, 034, 044, 072, etc.)

## 🔍 Key Findings

### Code Structure Mapping
```
Vendor: SYSTEM (XXX) - COMPONENT (XXX) - ASSEMBLY (XXX)
   ↓
VMRS:   SYSTEM (XXX) - ASSEMBLY (XXX) - COMPONENT (XXX)
   ↓
Match: 100% of unique constructed codes exist in VMRS
```

### Linking Strategies

1. **Direct Code Matching** (Highest Confidence)
   - 93.7% of parts with numeric codes match VMRS
   - 3,188 unique codes, all valid

2. **Keyword-Based Similarity** (Medium Confidence)
   - 1,890 shared keywords identified
   - TF-IDF and cosine similarity for fuzzy matching

3. **Hierarchical Traversal** (Structure-Based)
   - System → Assembly → Component relationships
   - 23 vendor classes map to VMRS system groups

4. **Manufacturer Linkage** (Brand-Specific)
   - 910 manufacturers in vendor data
   - VMRS Code Key 34 provides 5-char manufacturer codes

## 📈 Statistics

| Metric | Value |
|--------|-------|
| Total VMRS Codes | 66,729 |
| VMRS Systems | 289 |
| Total Vendor Parts | 29,710 |
| Parts with VMRS Codes | 18,327 (61.7%) |
| Matched Parts | 17,168 (93.7%) |
| Unique VMRS Codes Used | 3,188 |
| Code Validation Rate | 100% |
| Shared Keywords | 1,890 |
| Unique Manufacturers | 910 |

## 🛠️ Dependencies

See `requirements.txt`.

## 📝 Next Steps

1. **Build Knowledge Graph**
   - Import PoC dataset into graph database (Neo4j recommended)
   - Create nodes: VMRSSystem, VMRSAssembly, VMRSComponent, VendorPart, Manufacturer
   - Create relationships: PART_OF, MATCHES, MADE_BY, CATEGORIZED_AS

2. **Develop Query Interface**
   - Cypher queries for traversal
   - REST API for application access
   - Web UI for exploration

3. **Expand Coverage**
   - Process remaining 38% of vendor parts
   - Implement fuzzy matching for unmatched parts
   - Add manufacturer Code Key 34 mapping

4. **Validation & Refinement**
   - Subject matter expert review
   - Fix OCR errors in VMRS descriptions
   - Fill 3,254 empty VMRS descriptions

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

---

*Last Updated: January 21, 2026*  
*VMRS Version: 2.0*
