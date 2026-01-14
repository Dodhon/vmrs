# Plan: Generate Test Questions from Vendor Data

## Objective

Create a Python script that generates test questions from the vendor CSV with machine-generated oracle data for fast, consistent grading. The output aligns with `tests/test_questions/TEST_PLAN.md`.

## Definitions

- **Oracle**: The expected/correct answer for each test question. Generated automatically from source data.

- **Diverse selection**: When picking rows for questions, cycle through different SYSTEM_ or MANUFACTURER values to avoid clustering.

- **Row key**: A unique identifier for a source row, computed as `{PART}|{MANUFACTURER}`. Used to generate stable test IDs.

## Input

**Source CSV**: `vendor data/checked/Motors Part Cleanup - Return Data.csv`

All rows in this file are verified correct mappings. Use all rows (no filtering needed).

**CSV columns used**:
| Column | Description |
|--------|-------------|
| PART | Vendor part number |
| MANUFACTURER | Vendor/manufacturer name |
| DESCRIPTION | Part description text |
| VMRS | Full VMRS code (e.g., "001-001-062") |
| SYSTEM_ | System name |
| ASSEMBLY_ | Assembly name |
| COMPONENT_ | Component name |

## Outputs

**Question list**: `tests/test_questions/test_log.csv`

CSV columns:
- test_id: Stable identifier (hash-based)
- category: Question category
- expected_behavior: KNOWN_PRESENT, KNOWN_ABSENT, or AMBIGUOUS
- question_text: The question to ask
- row_key: Source row identifier (for traceability)
- expected_answer: Expected VMRS code(s)
- vendor_parts: Expected vendor parts (for VM category)
- pass_fail: Empty (filled during manual review)
- failure_type: Empty (filled during manual review)
- full_conversation: Empty (filled with complete conversation transcript during test execution)

## Categories

| Category | Template | Count | Expected Behavior |
|----------|----------|-------|-------------------|
| part_lookup | "What is the VMRS code for part number {PART}?" | 10 | KNOWN_PRESENT |
| vendor_lookup | "What is the VMRS code for {MANUFACTURER} part {PART}?" | 10 | KNOWN_PRESENT |
| description_exact | "What is the VMRS code for \"{DESCRIPTION}\"?" | 10 | KNOWN_PRESENT |
| description_partial | "What is the VMRS code for \"{PARTIAL_DESC}\"?" | 10 | KNOWN_PRESENT |
| hierarchy_navigation | "What is the hierarchy for VMRS code {VMRS}?" | 10 | KNOWN_PRESENT |
| vendor_mapping | "What vendor parts map to VMRS code {VMRS}?" | 10 | KNOWN_PRESENT |
| validation_valid | "Is {VMRS} a valid VMRS code?" | 5 | KNOWN_PRESENT |
| validation_invalid | "Is {VMRS} a valid VMRS code?" | 5 | KNOWN_ABSENT |
| comparison | "Do parts {PART_A} and {PART_B} have the same VMRS code?" | 10 | KNOWN_PRESENT |

Total: 80 questions

## Test ID Format

Stable IDs derived from row key hash:
- Format: `{PREFIX}-{HASH6}` where HASH6 is first 6 chars of SHA256 of row_key
- Example: `PN-a3f2c1`, `VP-b7d4e9`

Prefixes:
- PN = part_lookup
- VP = vendor_lookup
- DE = description_exact
- DP = description_partial
- HN = hierarchy_navigation
- VM = vendor_mapping
- VV = validation_valid
- VI = validation_invalid
- CP = comparison

## Ambiguity Policy

**part_lookup**: Filter out PART values that appear with multiple different VMRS codes across manufacturers. Only use unambiguous part numbers.

**vendor_lookup**: No ambiguity issue since MANUFACTURER+PART is unique.

**description_exact**: If a description maps to multiple VMRS codes, mark as AMBIGUOUS and list all acceptable codes in expected_answer.

## Step-by-Step Process

### Step 1: Load CSV Data

Read the vendor CSV file. For each row, compute row_key as `{PART}|{MANUFACTURER}`. Skip rows missing PART or VMRS.

### Step 2: Build Lookup Indexes

Create indexes for ambiguity detection:
- `part_to_vmrs`: Map each PART to set of VMRS codes it maps to
- `vmrs_to_parts`: Map each VMRS to list of (PART, MANUFACTURER) tuples

### Step 3: Generate Questions by Category

**part_lookup**:
- Filter to PART values that map to exactly one VMRS code (unambiguous)
- Select 10 rows with diverse SYSTEM_ values
- Oracle: expected_answer = the single VMRS code

**vendor_lookup**:
- Select 10 rows with diverse MANUFACTURER values
- Oracle: expected_answer = row's VMRS code

**description_exact**:
- Filter to rows with non-empty, unique descriptions
- Select 10 with diverse SYSTEM_ values
- Oracle: expected_answer = row's VMRS code

**description_partial**:
- Filter to rows with descriptions of 3+ words
- Select 10 with diverse SYSTEM_ values
- Truncate description to first N-1 words
- Oracle: expected_answer = row's VMRS code

**hierarchy_navigation**:
- Deduplicate rows by VMRS code
- Select 10 with diverse SYSTEM_ values
- Oracle: expected_answer = the VMRS code

**vendor_mapping**:
- Filter to VMRS codes with 2+ parts mapped
- Select 10
- Oracle: expected_answer = VMRS code, vendor_parts = all parts that map to it

**validation_valid**:
- Select 5 valid VMRS codes from the data
- Oracle: expected_answer = the valid code

**validation_invalid**:
- Generate 5 invalid VMRS codes by perturbation:
  - Take valid code, change last digit (e.g., 001-001-062 → 001-001-063)
  - Verify perturbed code does NOT exist in source data
- Oracle: expected_answer = empty (code should not exist)

**comparison**:
- 5 same-VMRS pairs: Pick two parts with SAME VMRS code
- 5 different-VMRS pairs: Pick two parts with DIFFERENT VMRS codes
- Oracle: expected_answer = both VMRS codes

### Step 4: Generate Stable Test IDs

For each question:
- Compute SHA256 hash of row_key (or row_keys for comparison)
- Take first 6 hex characters
- Combine with category prefix: `{PREFIX}-{HASH6}`

### Step 5: Write Output

Write CSV with columns: test_id, category, expected_behavior, question_text, row_key, expected_answer, vendor_parts, pass_fail, failure_type, full_conversation

The pass_fail, failure_type, and full_conversation columns are left empty for test execution.

## CLI Arguments

- `--vendor-csv`: Path to the vendor CSV file

## Constants

- Output: `tests/test_questions/test_log.csv`
- Count: 10 questions per category (5 for validation_valid/invalid)
- Seed: 42

## Handling CSV Updates

Test IDs are stable because they're derived from row_key hashes. When the CSV changes:
- Existing questions retain their test_id if the row_key still exists
- New rows get new test_ids
- Removed rows' test_ids become orphaned (detectable)

## Verification

After running:
1. Confirm test_log.csv has 80 rows
2. Verify each category has expected count
3. Verify expected_answer is populated for all KNOWN_PRESENT questions
4. Verify validation_invalid questions have VMRS codes that don't exist in source
5. Verify part_lookup questions use unambiguous part numbers
6. Check diversity: count unique SYSTEM_ and MANUFACTURER values used
