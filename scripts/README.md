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

## 🔍 Analysis Scripts (`analysis/`)

### 1. `linking_patterns_analysis.py`
**Purpose**: Analyze patterns between VMRS and vendor data to identify linking strategies

**Input**:
- `csv data/VMRS_COMPLETE_v20_MASTER.csv`
- `vendor data/Master Parts list for Richard 06.25.25 (1).csv`

**Output** (in `eda/`):
- `common_systems.csv` - System codes present in both datasets
- `vendor_vmrs_matched_codes.csv` - 17,168 matched parts
- `shared_keywords.csv` - 1,890 shared keywords with frequencies
- Console report with 6 pattern analyses

**Analysis**:
1. Direct system code matching
2. Vendor code construction to VMRS
3. Description keyword overlap
4. Class/category alignment
5. Hierarchical structure comparison
6. Manufacturer/brand codes

**Key Finding**: 93.7% match rate (17,168 out of 18,327 parts with numeric codes)

**Usage**:
```bash
python3 scripts/analysis/linking_patterns_analysis.py
```

---

### 2. `verify_code_alignment.py`
**Purpose**: Verify code alignment accuracy and create PoC-ready datasets

**Input**:
- `csv data/VMRS_COMPLETE_v20_MASTER.csv`
- `vendor data/Master Parts list for Richard 06.25.25 (1).csv`
- `eda/vendor_vmrs_matched_codes.csv`

**Output** (in `eda/`):
- `poc_dataset.csv` - System 044 PoC (639 parts, 355 HIGH quality)
- `perfect_alignment_poc.csv` - High-confidence matches (111 parts)
- Console report with quality breakdown

**Analysis**:
- Clarifies what 93.7% match means
- Identifies best systems for PoC
- Calculates description similarity scores
- Quality grades: HIGH (>0.30), MEDIUM (0.15-0.30), LOW (<0.15)

**Key Finding**: 
- 100% of unique constructed codes exist in VMRS
- System 044 (Fuel System) has 55.6% HIGH quality matches

**Usage**:
```bash
python3 scripts/analysis/verify_code_alignment.py
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

### Analysis (After Setup)
```bash
# 6. Analyze linking patterns
python3 scripts/analysis/linking_patterns_analysis.py

# 7. Verify and create PoC datasets
python3 scripts/analysis/verify_code_alignment.py
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
| linking_patterns_analysis.py | 3 analysis CSVs | 93.7% match rate |
| verify_code_alignment.py | 2 PoC datasets | 355 HIGH quality |

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

*Last Updated: September 30, 2025*
