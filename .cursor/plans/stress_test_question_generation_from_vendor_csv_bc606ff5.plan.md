---
name: Stress Test - Curated Edge Cases for Chat Interface
overview: Curate comprehensive edge case questions from vendor CSV to stress test the Claude Desktop + Neo4j MCP chat interface. Claude Code will analyze vendor data and hand-pick 200-300 edge cases across all failure categories. Deadline - Dec 15 meeting with David.
status: in_progress
deadline: 2025-12-15
todos:
  - id: analyze-vendor-data
    content: Analyze vendor CSV to identify edge case patterns (abbreviations, typos, ambiguous terms, missing data)
    status: pending
    output: None (analysis step)
  - id: curate-edge-cases
    content: Curate 200-300 edge case questions with expected answers, categorized by failure type
    status: pending
    output: tests/stress_test/curated_edge_cases.csv
    dependencies:
      - analyze-vendor-data
  - id: create-summary-doc
    content: Write summary documenting categories, expected failures, and testing procedure
    status: pending
    output: tests/stress_test/edge_cases_summary.md
    dependencies:
      - curate-edge-cases
  - id: create-github-issue
    content: Create GitHub issue with stress test plan, link to files, success criteria
    status: pending
    output: GitHub Issue (via gh CLI)
    dependencies:
      - create-summary-doc
---

# Stress Test Plan: Curated Edge Cases

## Goal (from presentation_notes.txt)
> "Make a test plan to stress test the capabilities of the solution"
> - needs to cover all possible edge cases
> - identify what questions will break the solution
> - make github issue for this
> - must be done by meeting w David on the 15th

## Approach
**Claude Code will curate the edge cases directly** by:
1. Analyzing the vendor CSV data for problematic patterns
2. Hand-picking 200-300 representative edge cases
3. Categorizing by failure type and risk level
4. Writing to CSV for easy testing

## Test Environment
- **Interface:** Claude Desktop + Neo4j MCP connector
- **Database:** Neo4j (75,595 nodes - VMRS + Vendor data)
- **Source:** `vendor data/checked/Motors Part Cleanup - Return Data.csv` (20,348 rows)

---

## Deliverables with Output Formats

| Todo | Output File | Format |
|------|-------------|--------|
| analyze-vendor-data | (none) | Analysis step only |
| curate-edge-cases | `tests/stress_test/curated_edge_cases.csv` | CSV |
| create-summary-doc | `tests/stress_test/edge_cases_summary.md` | Markdown |
| create-github-issue | GitHub Issue | `gh issue create` |

---

## Output File Specifications

### 1. curated_edge_cases.csv

**Path:** `tests/stress_test/curated_edge_cases.csv`

**Columns:**
```
id,category,subcategory,question,expected_vmrs,expected_behavior,risk_level,source_description,notes
```

**Example rows:**
```csv
id,category,subcategory,question,expected_vmrs,expected_behavior,risk_level,source_description,notes
DQ-001,data_quality,abbreviations,"What is the VMRS code for DRYER-RECEIVER W/DYE?",001-001-065,Should parse W/ as 'with',high,"DRYER-RECEIVER W/DYE",Tests abbreviation handling
AM-001,ambiguity,generic_term,"What is the VMRS code for SEAL?",MULTIPLE,Should ask for clarification or list options,critical,SEAL,Single word matches 50+ components
```

### 2. edge_cases_summary.md

**Path:** `tests/stress_test/edge_cases_summary.md`

**Structure:**
```markdown
# Edge Cases Summary
## Statistics
## Categories Breakdown
## Testing Procedure
## Success Criteria
## Known Failure Modes
```

### 3. GitHub Issue

**Created via:** `gh issue create`

**Title:** `[Testing] Stress Test Plan - Curated Edge Cases`

**Body includes:**
- Summary of approach
- Links to CSV and summary files
- Testing checklist
- Deadline: Dec 15

---

## Edge Case Categories

### Category A: Data Quality Issues (code: `data_quality`)
| Subcategory | Pattern | Risk |
|-------------|---------|------|
| `abbreviations` | W/, W/O, A/C, ASSY, LH, RH, P/S | High |
| `punctuation` | Multiple dashes, slashes, commas | High |
| `truncated` | Cut-off descriptions | High |
| `embedded_codes` | Part numbers in description | Medium |
| `ocr_errors` | WINSHIELD, MIRRIOR, CONDENSOR | High |

### Category B: Ambiguity Issues (code: `ambiguity`)
| Subcategory | Pattern | Risk |
|-------------|---------|------|
| `generic_term` | SEAL, SWITCH, BRACKET, FILTER | Critical |
| `partial_description` | Incomplete context | Critical |
| `multi_system` | Same part in different systems | High |

### Category C: Missing/Invalid Data (code: `missing_data`)
| Subcategory | Source | Count |
|-------------|--------|-------|
| `neo4j_gaps` | Previous test failures | 5 codes |
| `unclassified` | VMRS='nan' | 373 rows |
| `unable_to_code` | NOTES field | 81 rows |

### Category D: Query Complexity (code: `query_complexity`)
| Subcategory | Pattern | Risk |
|-------------|---------|------|
| `multi_result` | Returns 100s of items | Critical |
| `reverse_lookup` | VendorPart → Component | High |
| `cross_system` | Spans multiple systems | High |
| `hierarchy` | Navigate up/down tree | Medium |

### Category E: Natural Language (code: `natural_language`)
| Subcategory | Pattern | Risk |
|-------------|---------|------|
| `informal` | "whats the code for..." | Medium |
| `typos` | "brakke pade" | High |
| `synonyms` | AC vs A/C vs air conditioning | Medium |

### Category F: Boundary Conditions (code: `boundary`)
| Subcategory | Pattern | Risk |
|-------------|---------|------|
| `minimal_input` | Single word or character | Medium |
| `long_input` | 100+ character queries | Low |
| `special_chars` | /, -, #, &, () | Medium |
| `nonexistent` | Made-up parts | Medium |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Edge cases curated | 200-300 questions |
| Categories covered | All 6 (A-F) |
| Risk levels covered | All (critical, high, medium, low) |
| Manual testing | Run 50-100 through Claude Desktop |
| Failures documented | Catalog what breaks |

