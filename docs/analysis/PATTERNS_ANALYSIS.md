# VMRS Data Pattern Analysis

## Overview
Analysis of 66,729 VMRS (Vehicle Maintenance Reporting Standards) records from the master CSV.

---

## 1. HIERARCHICAL CODE STRUCTURE

### Three-Level Hierarchy
The VMRS uses a strict hierarchical coding system:

```
SYSTEM (XXX) 
  └─> ASSEMBLY/SUBCODE (XXX)
       └─> COMPONENT (XXX)
```

### Code Formats
- **9-digit codes**: `XXX-XXX-XXX` (System-Assembly-Component)
  - Example: `001-002-064` = System 001, Assembly 002, Component 064
  - 89.4% of all records (59,650 codes)
  - Represents specific components

- **6-digit codes**: `XXX-XXX` (System-Assembly)
  - Example: `001-002` = System 001, Assembly 002
  - 10.6% of all records (7,079 codes)
  - Represents assembly-level items

### Key Structural Patterns
1. **Perfect hierarchy alignment**: 100% of codes follow the hierarchy
   - First segment ALWAYS matches the `system` column
   - Second segment ALWAYS matches the `subcode` column
   
2. **Mutually exclusive**: Records contain EITHER a 9-digit OR 6-digit code, never both

3. **Reserved codes**: `XXX-XXX-000` appears 3,094 times (often assembly-level or generic items)

---

## 2. SYSTEM DISTRIBUTION

### Top 20 Systems by Record Count
| System | Records | % of Total |
|--------|---------|------------|
| 002 | 8,517 | 12.8% |
| 013 | 2,927 | 4.4% |
| 174 | 2,794 | 4.2% |
| 082 | 2,336 | 3.5% |
| 053 | 2,320 | 3.5% |
| 044 | 2,061 | 3.1% |
| 045 | 1,916 | 2.9% |
| 027 | 1,843 | 2.8% |
| 016 | 1,811 | 2.7% |
| 043 | 1,772 | 2.7% |
| 055 | 1,704 | 2.6% |
| 034 | 1,519 | 2.3% |
| 001 | 1,493 | 2.2% |
| 026 | 1,357 | 2.0% |
| 015 | 1,297 | 1.9% |
| 042 | 1,233 | 1.8% |
| 071 | 1,171 | 1.8% |
| 014 | 1,022 | 1.5% |
| 003 | 1,017 | 1.5% |
| 059 | 979 | 1.5% |

### Hierarchy Statistics
- **Total systems**: 289
- **Average subcodes per system**: 13.2
- **Total system-subcode combinations**: 2,035
- **Average components per system-subcode**: 17.6

---

## 3. DESCRIPTION PATTERNS

### Common Component Types (from description prefixes)
Top 15 most common component categories:
1. **Hardware, Mounting** (100+ occurrences) - Fasteners and mounting hardware
2. **Support** (59) - Structural support components
3. **Cover** (56) - Protective covers
4. **Mounting Bracket** (52) - Brackets for mounting
5. **Frame** (49) - Frame components
6. **Switch** (46) - Electrical switches
7. **Seal** (44) - Sealing components
8. **Control** (42) - Control mechanisms
9. **Bracket** (40) - Generic brackets
10. **Panel** (38) - Panel components
11. **Wiring Harness** (37) - Electrical wiring
12. **Controls** (36) - Control systems
13. **Hydraulic System** (34) - Hydraulic components
14. **Plate** (33) - Plate components
15. **Motor** (29) - Motor assemblies

---

## 4. DATA QUALITY ISSUES

### Empty Descriptions
- **3,254 records** (4.9%) have empty descriptions
- Primarily in newer or less-documented codes

### OCR/Typo Patterns
Common data quality issues found (likely from OCR conversion):
- "Dus" instead of "Bus" (e.g., `174-001-117`)
- "Salety" instead of "Safety" (e.g., `174-001-143`)
- "Lett" instead of "Left"
- "Dody" instead of "Body"
- "Laten" instead of "Latch"
- "Colled" instead of "Coiled"
- Various spacing and capitalization inconsistencies

---

## 5. SOURCE FILE DISTRIBUTION

### File Coverage
- **36 unique source files** (from markdown documents)
- Records distributed relatively evenly across source files
- Average ~1,853 records per source file

### Top Source Files
| Source File | Records |
|-------------|---------|
| page 5_pages_76-100.md | 3,377 |
| page 5_pages_26-50.md | 3,363 |
| page 6_pages_76-100.md | 3,319 |
| page 6_pages_26-50.md | 3,303 |
| page 7_pages_1-25.md | 3,289 |

---

## 6. CODE RANGE COVERAGE

### Full Spectrum
- **First code**: `000-000-000`
- **Last code**: `999-999-999`
- System codes span from 000 to 999 (full 3-digit range)
- Not all codes are populated (gaps exist for future use)

---

## 7. EXAMPLE HIERARCHY

### System 001: Air Conditioning, Heating & Ventilating
Total records: 1,493

**Assembly 001-000**: Crusher Assembly
- 6-digit code: `001-000` (assembly level)
- 31 component-level codes (9-digit)

**Assembly 001-001**: Air Conditioning
- 438 component-level codes
- Includes: compressors, accumulators, adapters, valves, etc.

**Assembly 001-002**: Heating & Ventilating
- 194 component-level codes
- Includes: actuators, heaters, motors, plenums, etc.

---

## 8. KEY INSIGHTS

1. **Highly Structured**: VMRS is a rigorously organized hierarchical system with perfect code alignment
2. **Component-Heavy**: 89% of codes are at the component level (9-digit)
3. **Comprehensive Coverage**: Spans 289 systems with deep component-level detail
4. **Standardized Naming**: Component descriptions follow consistent patterns (type - location/function)
5. **Quality Issues**: ~5% empty descriptions and scattered OCR errors need cleanup
6. **Bus-Centric**: Many codes reference bus components (reflects source material)
7. **Reserved Ranges**: XXX-XXX-000 codes serve as assembly-level grouping codes

---

## 9. RECOMMENDED NEXT STEPS

1. **Data Cleanup**: Fix OCR errors and standardize descriptions
2. **Fill Empty Descriptions**: Research and populate 3,254 missing descriptions
3. **Create Lookup Tools**: Build search/browse interfaces leveraging the hierarchy
4. **Validation**: Cross-reference with official VMRS documentation
5. **Categorization**: Group systems into higher-level categories (e.g., powertrain, body, electrical)

