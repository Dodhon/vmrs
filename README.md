# VMRS Data Processing & Analysis

A comprehensive toolkit for processing, analyzing, and linking Vehicle Maintenance Reporting Standards (VMRS) data with vendor parts data.

## 📁 Project Structure

```
vrms/
├── README.md                          # This file
│
├── scripts/                           # Python scripts
│   ├── data_processing/               # Data extraction and transformation
│   │   ├── extract_vmrs_to_csv.py    # Extract VMRS codes from markdown
│   │   ├── combine_vmrs_csv.py       # Combine multiple CSV files
│   │   ├── validate_vmrs_csv.py      # Data validation
│   │   ├── sort_master_csv.py        # Sort master data
│   │   ├── excel_to_csv.py           # Convert Excel to CSV
│   │   └── sort_vendor_csv.py        # Sort vendor data by columns
│   │
│   └── analysis/                      # Data analysis scripts
│       ├── linking_patterns_analysis.py    # Find patterns between VMRS and vendor data
│       └── verify_code_alignment.py        # Verify code matches and create PoC datasets
│
├── docs/                              # Documentation
│   └── analysis/                      # Analysis reports
│       ├── PATTERNS_ANALYSIS.md      # VMRS data pattern analysis
│       ├── LINKING_PATTERNS.md       # VMRS-to-vendor linking strategies
│       ├── POC_READY_SUBSETS.md      # PoC-ready datasets documentation
│       └── QUICK_STATS.txt           # Quick statistics summary
│
├── csv data/                          # Processed VMRS CSV data
│   ├── VMRS_COMPLETE_v20_MASTER.csv  # Master VMRS dataset (66,729 codes)
│   ├── validation_report.json        # Validation results
│   ├── validation_summary.json       # Validation summary
│   ├── master_summary.json           # Master dataset summary
│   └── [source CSV files...]         # Original extracted CSVs
│
├── md data/                           # Source markdown files
│   └── [39 VMRS handbook pages]      # Original VMRS documentation
│
├── vendor data/                       # Vendor parts data
│   ├── Master Parts list for Richard 06.25.25 (1).xlsx    # Original Excel
│   ├── Master Parts list for Richard 06.25.25 (1).csv     # Converted CSV
│   └── Master_Parts_sorted_by_*.csv  # Sorted by each column
│
└── eda/                               # Exploratory data analysis
    ├── VMRS_COMPLETE_v20_MASTER.csv           # Copy of master VMRS
    ├── VMRS_MASTER_sorted_by_*.csv            # Sorted VMRS data
    ├── vendor_vmrs_matched_codes.csv          # 17,168 matched parts
    ├── common_systems.csv                      # Common system codes
    ├── shared_keywords.csv                     # Shared keywords analysis
    ├── poc_dataset.csv                         # System 044 PoC dataset (639 parts)
    └── perfect_alignment_poc.csv               # High-confidence matches (111 parts)
```

## 📊 Key Datasets

### VMRS Data
- **66,729 codes** across 289 systems
- **89.4%** component-level (9-digit codes)
- **10.6%** assembly-level (6-digit codes)
- **Hierarchical structure**: System → Assembly → Component

### Vendor Data
- **29,710 parts** from 910 manufacturers
- **18,327 parts** (61.7%) have complete VMRS codes
- **17,168 parts** (93.7%) match existing VMRS codes
- **3,188 unique VMRS codes** used

### Linkage Success
- **100%** of constructed codes exist in VMRS
- **355 HIGH-quality matches** in System 044 (Fuel System)
- **111 perfect alignment** matches across systems

## 🚀 Quick Start

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

### 2. Analysis

```bash
# Analyze linking patterns between VMRS and vendor data
python3 scripts/analysis/linking_patterns_analysis.py

# Verify code alignment and create PoC datasets
python3 scripts/analysis/verify_code_alignment.py
```

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

```bash
pip3 install pandas openpyxl
```

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

*Last Updated: September 30, 2025*  
*VMRS Version: 2.0*
