# Vendor Parts vs Extraction Runs - Comparison Findings

## Data Filtering
- **Vendor filter**: COMPLETE VMRS = YES, numeric codes only (no letters)
- **Vendor parts analyzed**: 17,187 parts (57.8% of total 29,710)
- **Vendor codes**: 88 systems, 1,809 assemblies, 2,874 components

## System-Level Coverage

| Run | Coverage | Missing |
|-----|----------|---------|
| **Previous** | **100.0%** (88/88) | 0 |
| Current | 78.4% (69/88) | 19 |
| Combined | **100.0%** (88/88) | 0 |

**Finding**: Previous extraction covers all numeric vendor systems. Current run missing 19 systems.

## Assembly-Level Coverage

| Run | Coverage | Missing |
|-----|----------|---------|
| **Previous** | **24.0%** (434/1,809) | 1,375 |
| Current | 2.1% (38/1,809) | 1,771 |
| Combined | **24.0%** (435/1,809) | 1,374 |

**Finding**: Previous run is 11x better. 76.0% of vendor assemblies not found in either extraction.

## Component-Level Coverage

| Run | Coverage | Missing |
|-----|----------|---------|
| **Previous** | 0.0% (1/2,874) | 2,873 |
| **Current** | **0.3%** (10/2,874) | 2,864 |
| Combined | **0.3%** (10/2,874) | 2,864 |

**Finding**: Both runs have very low component overlap. 99.7% of vendor components not found.

## Key Findings

1. **System Coverage**: Perfect (100%) - All numeric vendor systems covered by previous extraction
2. **Assembly Gap**: 76.0% missing - Vendor uses many assemblies not documented in handbooks
3. **Component Gap**: 99.7% missing - Vendor component structure differs significantly from handbook
4. **Best Run**: Previous extraction better for systems (100%) and assemblies (24.0%); current run slightly better for components (0.3% vs 0.0%)

## Top Vendor Systems (by part count)
- System 266: 2,511 parts (Previous only)
- System 013: 1,798 parts (Both)
- System 002: 1,293 parts (Both)
- System 034: 1,003 parts (Both)
- System 043: 890 parts (Both)

## Top Vendor Assemblies (by part count)
- 032-001: 217 parts (Previous only)
- 041-005: 153 parts (Neither)
- 045-001: 148 parts (Previous only)
- 016-001: 121 parts (Previous only)
- 013-023: 120 parts (Neither)

## Extraction Codes Not in Vendor
- Current: 47 systems (e.g., 067, 069, 074, 075, 076, 096, 121, 141, 143, 152-169)
- Previous: 70 systems
- These handbook systems are not used in vendor parts data

## Recommendations
1. Use previous extraction for system/assembly matching (100% system, 24% assembly coverage)
2. Component matching requires vendor-specific mapping (99.7% gap indicates structural differences)
3. Consider hybrid approach: previous for systems/assemblies, current for component-level narrative detail

