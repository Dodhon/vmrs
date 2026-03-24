# GitHub Copilot Instructions for VRMS Project

## Project Overview

This repository contains a comprehensive toolkit for processing, analyzing, and linking **Vehicle Maintenance Reporting Standards (VMRS)** data with vendor parts data. The project builds a knowledge graph connecting VMRS hierarchy (Systems → Assemblies → Components) with vendor part catalogs.

### Mission
Build and validate a dependable bridge between VMRS standards and vendor part data so stakeholders can query (via Neo4j) and trust the answers.

---

## Project Structure

```
vrms/
├── src/                    # Core Python modules
│   ├── text_chunker.py     # Document chunking for LLM processing
│   ├── triple_extractor.py # Claude-based structured extraction
│   ├── neo4j_client.py     # Neo4j database operations
│   ├── graph_builder.py    # Pipeline orchestrator
│   └── file_stats.py       # File utility functions
│
├── scripts/                # Data processing and import scripts
│   ├── data_processing/    # ETL scripts for CSV/Excel processing
│   │   ├── extract_vmrs_to_csv.py
│   │   ├── combine_vmrs_csv.py
│   │   ├── validate_vmrs_csv.py
│   │   ├── sort_master_csv.py
│   │   ├── excel_to_csv.py
│   │   └── sort_vendor_csv.py
│   ├── neo4j_import.py     # Import JSON to Neo4j
│   ├── import_csv_to_neo4j.py
│   ├── run_ingest_from_file.py  # Main extraction script
│   └── run_graph_extraction.py
│
├── docs/                   # Documentation
│   └── analysis/           # Data analysis reports
│
├── csv data/               # VMRS CSV data (66,729 codes)
├── md data/                # Source VMRS markdown files
├── vendor data/            # Vendor parts data (29,710 parts)
├── eda/                    # Exploratory data analysis outputs
├── llm_matching/           # LLM matching context files
├── tests/                  # Test files
└── knowledge_graph_output/ # Extraction outputs (gitignored)
```

---

## Key Data Concepts

### VMRS Code Structure
- **System codes** (Code Key 31): 3 digits (e.g., `044` = Fuel System)
- **Assembly codes** (Code Key 32): 6 digits (e.g., `044-001` = Fuel Injection)
- **Component codes** (Code Key 33): 9 digits (e.g., `044-001-015` = Fuel Injector)
- **Hierarchy**: Component → Assembly → System (PART_OF relationships)

### Vendor Data Mapping
```
Vendor Format:  SYSTEM (XXX) - COMPONENT (XXX) - ASSEMBLY (XXX)
VMRS Format:    SYSTEM (XXX) - ASSEMBLY (XXX) - COMPONENT (XXX)
```

---

## Coding Conventions

### Python Style
- Use **Python 3** with type hints where applicable
- Use `logging` module for output (not print statements in library code)
- Follow PEP 8 style guidelines
- Use docstrings for all public functions and classes

### Module Patterns

#### For scripts (executable files):
```python
#!/usr/bin/env python3
"""
Script description.

Usage:
  python3 scripts/script_name.py [args]
"""

import os
import sys
from pathlib import Path

def main():
    """Main entry point."""
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

#### For library modules:
```python
"""
Module description - brief functionality overview.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ClassName:
    """Class description with purpose."""
    
    def __init__(self, param: str):
        """
        Initialize with parameters.
        
        Args:
            param: Description of parameter
        """
        self.param = param
    
    def method_name(self, arg: str) -> Dict:
        """
        Method description.
        
        Args:
            arg: Description
            
        Returns:
            Dictionary with results
        """
        pass
```

### Error Handling
- Use try/except with specific exception types
- Log errors with `logger.error()` including context
- Gracefully handle missing files and invalid data
- Return empty results rather than crashing when possible

### Code Validation Patterns
```python
# VMRS code validation
def is_valid_system_code(code: str) -> bool:
    """System code: 3 digits, range 001-999"""
    if not code or "-" in code:
        return False
    try:
        return 1 <= int(code) <= 999
    except ValueError:
        return False

def is_valid_assembly_code(code: str) -> bool:
    """Assembly code: XXX-XXX format"""
    return code and code.count("-") == 1 and all(
        part.isdigit() and len(part) == 3 for part in code.split("-")
    )

def is_valid_component_code(code: str) -> bool:
    """Component code: XXX-XXX-XXX format"""
    return code and code.count("-") == 2 and all(
        part.isdigit() and len(part) == 3 for part in code.split("-")
    )
```

---

## Dependencies

### Core Dependencies
```bash
pip3 install pandas openpyxl        # Data processing
pip3 install anthropic              # Claude API for LLM extraction
pip3 install neo4j                  # Graph database
pip3 install python-dotenv          # Environment variables
```

### Install All
```bash
pip3 install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file (never commit this):
```bash
# Required for LLM extraction
ANTHROPIC_API_KEY=your_api_key_here

# Required for Neo4j storage
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Optional settings
LOG_LEVEL=INFO
```

---

## Common Workflows

### 1. Data Processing Pipeline
```bash
# Extract VMRS from markdown
python3 scripts/data_processing/extract_vmrs_to_csv.py

# Combine into master dataset
python3 scripts/data_processing/combine_vmrs_csv.py

# Validate data quality
python3 scripts/data_processing/validate_vmrs_csv.py

# Convert vendor Excel to CSV
python3 scripts/data_processing/excel_to_csv.py
```

### 2. Knowledge Graph Extraction
```bash
# Set PYTHONPATH and run extraction
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md

# Resume from checkpoint
PYTHONPATH=. python3 scripts/run_ingest_from_file.py \
  --input llm_matching/matching_context.md \
  --start-chunk 50
```

### 3. Neo4j Import
```bash
# Import JSON to Neo4j
PYTHONPATH=. python3 scripts/neo4j_import.py knowledge_graph_output/knowledge_graph.json

# Import CSV directly
python3 scripts/import_csv_to_neo4j.py --csv "csv data/VMRS_COMPLETE_v20_MASTER.csv"
```

---

## Neo4j Query Examples

```cypher
// Count entities
MATCH (s:System) RETURN count(s) as systems;
MATCH (a:Assembly) RETURN count(a) as assemblies;
MATCH (c:Component) RETURN count(c) as components;

// Find assemblies in Fuel System (044)
MATCH (a:Assembly)-[:PART_OF]->(s:System {code: "044"})
RETURN a.code, a.name;

// Get full hierarchy for a component
MATCH path = (c:Component {code: "044-001-015"})-[:PART_OF*]->(s:System)
RETURN path;

// Find components under an assembly
MATCH (c:Component)-[:PART_OF]->(a:Assembly {code: "044-001"})
RETURN c.code, c.name;
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `csv data/VMRS_COMPLETE_v20_MASTER.csv` | Master VMRS dataset (66,729 codes) |
| `vendor data/Master Parts list*.csv` | Vendor parts (29,710 parts) |
| `eda/poc_dataset.csv` | System 044 PoC dataset (639 parts) |
| `eda/perfect_alignment_poc.csv` | High-confidence matches (111 parts) |
| `llm_matching/matching_context.md` | VMRS context for LLM extraction |
| `docs/project_context.md` | AI agent context document |

---

## Testing Guidelines

### Running Tests
```bash
# Run from project root
python3 -m pytest tests/
```

### Test File Locations
- Unit tests: `tests/`
- Acceptance tests: `tests/neo4j_acceptance/`

### Test Patterns
- Name test files as `test_*.py`
- Use descriptive test function names: `test_valid_system_code_returns_true`
- Mock external dependencies (Neo4j, Anthropic API)

---

## Important Notes

### Data Reliability
- Handbook-derived VMRS data is authoritative
- Vendor codes should be verified against handbook before use
- The KG source chain: handbook → LLM extraction → CSV → Neo4j

### LLM Extraction
- Uses Claude Sonnet 4.5 for structured extraction
- Temperature=0 for deterministic results
- Chunk size: ~2000 tokens with 200 token overlap
- Progress checkpoints saved for resumption

### Code as Primary Keys
- VMRS codes are unique and canonical
- Prefer codes over names (names may have OCR errors)
- Enable vendor matching through code alignment

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run with `PYTHONPATH=.` prefix |
| Neo4j connection error | Check credentials in `.env`, verify Neo4j is running |
| JSON parsing errors | LLM may return malformed JSON; check logs, retry chunk |
| Missing environment variable | Create `.env` file with required keys |
| File path errors | Run scripts from project root directory |

---

## Contributing Guidelines

1. **Follow existing patterns** - Match the style of nearby code
2. **Add docstrings** - Document all public functions and classes
3. **Validate VMRS codes** - Use validation helpers before processing
4. **Handle errors gracefully** - Log and continue rather than crash
5. **Test changes** - Add tests for new functionality
6. **Update documentation** - Keep READMEs in sync with changes

---

*Last Updated: November 2025*
