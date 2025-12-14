# Edge Cases Summary

**Generated:** 2025-12-13
**Total Edge Cases:** 224
**Source:** `vendor data/checked/Motors Part Cleanup - Return Data.csv` (20,348 parts)
**Test Interface:** Claude Desktop + Neo4j MCP

---

## Statistics by Category

| Category | Code | Count | Description |
|----------|------|-------|-------------|
| Data Quality | DQ | 40 | Abbreviations, spelling errors, punctuation, embedded codes, truncated text |
| Ambiguity | AM | 30 | Generic terms, partial descriptions, multi-system parts |
| Missing Data | MD | 20 | Known Neo4j gaps, unclassified parts, unable to verify |
| Query Complexity | QC | 22 | Multi-result, reverse lookup, cross-system, hierarchy, comparison |
| Natural Language | NL | 27 | Informal, typos, synonyms, case variations |
| Boundary | BD | 25 | Minimal input, long input, special chars, nonexistent, malformed, empty |
| Manufacturer | MF | 10 | Lookup, part number, variations |
| Vendor Query | VQ | 30 | Who sells, specific vendor, comparison, availability |
| Not In Database | NE | 20 | Fake vendors, fake parts, fake VMRS codes, irrelevant queries |

---

## Category Details

### Data Quality (DQ-001 to DQ-040)

**Subcategories:**
- `abbreviations` (10): W/, W/O, A/C, ASSY, LH, RH, P/S, ASM
- `spelling_errors` (8): CONDENSOR, WINSHIELD, MIRRIOR, SEPERATOR, COONECTOR
- `punctuation` (7): Heavy commas, mixed punctuation, inconsistent spacing
- `embedded_codes` (7): Part numbers, specs, dimensions in descriptions
- `truncated` (8): Cut-off descriptions, duplicate words

**Why these break the system:**
- NLP parsing struggles with non-standard abbreviations
- Spelling errors don't match indexed terms
- Punctuation interferes with tokenization

---

### Ambiguity (AM-001 to AM-030)

**Subcategories:**
- `generic_term` (20): SEAL, SWITCH, BRACKET, HOSE, GASKET, BOLT, etc.
- `partial_description` (5): BATTERY, FLANGE, TERMINAL, RETAINER, SPRING
- `multi_system` (5): Parts appearing across multiple VMRS systems

**Why these break the system:**
- Single words match 20-100+ different VMRS codes
- System needs to ask clarifying questions
- Without context, any answer could be wrong

**Critical cases:**
- "SEAL" → 304 parts across 19 systems, 106 unique VMRS codes
- "HOSE" → 534 parts across 17 systems, 111 unique VMRS codes
- "SWITCH" → 280 parts across 24 systems, 90 unique VMRS codes

---

### Missing Data (MD-001 to MD-020)

**Subcategories:**
- `vendor_sourced` (6): Components created from vendor data (not in VMRS handbook)
- `unclassified` (9): Parts vendor marked "UNABLE TO CODE"
- `unable_to_verify` (5): Parts with uncertain classification

**Vendor-Sourced Components:**
These codes exist in vendor CSV but not in VMRS handbook. They were created by `fix_orphaned_vendor_parts.py`:
- `001-004-064`: VENT - CAB EXHAUSTER, SLEEPER (3 vendor parts)
- `002-017-014`: SILL - OUTER (1 vendor part)
- `032-001-001`: BATTERY (237 vendor parts)

**Why these test the system:**
- Tests if system can find vendor-sourced components
- Unclassified parts should return "not found" gracefully
- Unable to verify parts may have uncertain answers

---

### Query Complexity (QC-001 to QC-022)

**Subcategories:**
- `multi_result` (5): Queries returning 100s-1000s of results
- `reverse_lookup` (5): VendorPart → Component lookups
- `cross_system` (5): Parts spanning multiple systems
- `hierarchy` (5): Traversing up/down VMRS tree
- `comparison` (2): Comparing two components

**Why these break the system:**
- Large result sets overwhelm the interface
- Need pagination or summarization
- Graph traversal queries may timeout

**Critical cases:**
- "List all brake-related parts" → 2,591 parts
- "What vendor parts map to 032-001-001?" → 237 parts

---

### Natural Language (NL-001 to NL-027)

**Subcategories:**
- `informal` (8): Casual language, slang, terse queries
- `typos` (7): Common misspellings in queries
- `synonyms` (8): British vs American English, abbreviations
- `case_variation` (4): UPPER, lower, Title, mIxEd case

**Why these break the system:**
- Informal queries may not match formal VMRS terminology
- Typos need fuzzy matching
- Synonyms require semantic understanding

---

### Boundary Conditions (BD-001 to BD-025)

**Subcategories:**
- `minimal_input` (5): Single character, two characters, terse
- `long_input` (2): 100+ character descriptions
- `special_chars` (6): Fractions, hashes, parentheses, ampersands
- `nonexistent` (5): Fictional parts (flux capacitor, warp drive)
- `malformed` (5): Invalid VMRS code formats
- `empty` (2): Empty or whitespace-only queries

**Why these break the system:**
- Edge cases test input validation
- System should handle gracefully without crashing
- Good test of robustness

---

### Manufacturer (MF-001 to MF-010)

**Subcategories:**
- `lookup` (3): Manufacturer + part type queries
- `part_number` (3): OEM part number lookups
- `variations` (4): Manufacturer name variations (GM, International)

**Why these break the system:**
- Part numbers may not be indexed
- Manufacturer abbreviations need mapping
- Cross-reference queries are complex

---

### Vendor Query (VQ-001 to VQ-030)

**Subcategories:**
- `who_sells` (15): "Which vendors sell X?" queries
- `specific_vendor` (7): "Does Vendor Y sell X?" queries
- `comparison` (3): Comparing vendors' offerings
- `availability` (3): Complex availability queries
- `informal` (2): Informal vendor queries

**Why these break the system:**
- Requires aggregating across vendor data
- Need to count and rank results
- Comparison queries need multiple lookups

**High-volume examples:**
- Battery → 35 vendors
- Brake pads → 32 vendors
- Electrical connectors → 31 vendors

---

## Testing Procedure

### Manual Testing Protocol

1. **Setup**
   - Open Claude Desktop
   - Verify Neo4j MCP connection
   - Have `curated_edge_cases.csv` open

2. **For each test:**
   - Copy question from CSV
   - Paste into Claude Desktop
   - Record response
   - Compare to `expected_vmrs` and `expected_behavior`
   - Classify result

3. **Result Classification:**

| Result | Definition |
|--------|------------|
| PASS | Correct VMRS code returned |
| PARTIAL | Correct system/assembly but wrong component |
| FAIL | Wrong VMRS code returned |
| NOT_FOUND_OK | System correctly said "not found" for missing data |
| CLARIFIED | System asked appropriate clarifying question |
| ERROR | System error or unexpected behavior |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Data Quality tests passing | >70% |
| Ambiguity handled correctly | System asks for clarification |
| Missing data handled | Returns "not found" gracefully |
| Query complexity | Summarizes large results |
| Natural language | >80% correct |
| Boundary conditions | No crashes, graceful errors |
| Vendor queries | Returns relevant vendor lists |

---

## Expected Failure Modes

### High Priority Failures (must fix before demo)
1. **Ambiguous queries returning wrong single answer** (should ask to clarify)
2. **Large result sets crashing interface** (should paginate/summarize)
3. **Known Neo4j gaps returning hallucinated data** (should say "not found")

### Medium Priority (document as known limitations)
1. Spelling errors not matched
2. British English synonyms not recognized
3. Part number lookups not working

### Low Priority (future improvements)
1. Case sensitivity issues
2. Very long queries truncated
3. Special character handling

---

## Files Reference

| File | Description |
|------|-------------|
| `tests/stress_test/curated_edge_cases.csv` | 205 curated test questions |
| `tests/stress_test/edge_cases_summary.md` | This document |
| `tests/neo4j_acceptance/questions.json` | Original 50 acceptance tests |
| `tests/neo4j_acceptance/summary_report.txt` | Previous test results (84% pass) |
