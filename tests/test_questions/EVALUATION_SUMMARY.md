## VMRS interface evaluation summary (stakeholder-readable)

This document summarizes what was tested, using exactly the inputs listed below, and what passed/failed.

### Exactly what inputs were tested

- **Test cases (questions + results)**: `tests/test_questions/test_log.csv`
  - Contains the **80 questions** that were asked.
  - Contains each test’s **expected answer** and the final **pass/fail** after evaluation.
  - Contains the exact **transcript file path** for every question in the `full_conversation` column.

- **Evidence (what the system actually answered)**: `tests/test_questions/conversations/*.md`
  - One file per `test_id`, containing the **full interaction**: the question, the Neo4j queries, the query results, and the assistant’s final answer.

- **Ground truth used for scoring (vendor → VMRS mapping)**: `vendor data/checked/Motors Part Cleanup - Return Data.csv`
  - This file was used as the **oracle** to compute expected VMRS codes and to verify vendor-part lists.
  - Important: this is **vendor mapping ground truth**, not the full official VMRS handbook.

### Exactly how the questions were phrased

These results are based on **80 predefined questions** (not free-form). Below are the **exact question templates** used in this test run.

Important details about wording:
- In transcripts, each prompt was prefixed with `[TEST_ID: <id>]` for tracking. The **end-user question text** is the part that comes after the prefix (it matches the `question_text` column in `tests/test_questions/test_log.csv`).
- VMRS codes were always asked in full 3-part form like `042-002-001` (no prefix-only questions like “042-002”).
- Description-based questions always used **quoted text**, e.g., `"GAUGE, FUEL"`.

Templates + examples:
- **Part number lookup** (`part_lookup`)
  - Template: `What is the VMRS code for part number <PART>?`
  - Example tested: `What is the VMRS code for part number 2234788PE?`

- **Vendor + part number lookup** (`vendor_lookup`)
  - Template: `What is the VMRS code for <MANUFACTURER> part <PART>?`
  - Example tested: `What is the VMRS code for WALTCO LIFT CORP part WO-10099360?`

- **Description (exact text)** (`description_exact`)
  - Template: `What is the VMRS code for "<DESCRIPTION>"?`
  - Example tested: `What is the VMRS code for "GAUGE, FUEL"?`

- **Description (partial text)** (`description_partial`)
  - Template: `What is the VMRS code for "<PARTIAL_DESCRIPTION>"?`
  - How the partial description text was created:
    - Start from a real vendor row’s **full** `DESCRIPTION` value in the vendor CSV.
    - Only use descriptions with **3+ words** (words are split on spaces).
    - Create the partial text by **removing the final word only** (everything else stays the same, including commas/punctuation attached to words).
    - Example: full description **`DRIVERS SIDE SEAT BELT`** → partial description **`DRIVERS SIDE SEAT`**.
    - This intentionally makes the query slightly less specific (and sometimes ambiguous) while still being close to what a user might type.
  - Example tested: `What is the VMRS code for "DRIVERS SIDE SEAT"?`

- **Hierarchy lookup** (`hierarchy_navigation`)
  - Template: `What is the hierarchy for VMRS code <VMRS_CODE>?`
  - Example tested: `What is the hierarchy for VMRS code 044-001-001?`

- **Vendor mapping from VMRS code** (`vendor_mapping`)
  - Template: `What vendor parts map to VMRS code <VMRS_CODE>?`
  - Example tested: `What vendor parts map to VMRS code 042-002-001?`

- **VMRS validity check** (`validation_valid` and `validation_invalid`)
  - Template: `Is <VMRS_CODE> a valid VMRS code?`
  - Example tested: `Is 001-001-049 a valid VMRS code?`

- **Comparison (same VMRS?)** (`comparison`)
  - Template: `Do parts <PART_A> and <PART_B> have the same VMRS code?`
  - Example tested: `Do parts HG0067 and S-32097 have the same VMRS code?`

What was **not** tested (examples):
- Alternate phrasings like “What VMRS code does <part> map to?”, “Find VMRS for…”, “VMRS of…”, etc.
- Asking without quotes (e.g., `What is the VMRS code for GAUGE, FUEL?`).
- Typos, abbreviations, or synonyms (“driver seatbelt” vs “drivers side seat belt”), unless they happened to occur in the predefined description text.
- Multi-part follow-ups in a single conversation (each test is a single question with a single answer).

### Gaps and recommended additions (next iteration)

Biggest gaps (especially for **1–2 word descriptions**):
- **Short-description coverage is structurally missing**: `description_partial` explicitly filters to **3+ words** and only removes the final word, so we never test 1-word or 2-word description lookups (common in real usage and typically more ambiguous).
- **“AMBIGUOUS” behavior is untested**: this run includes no cases where the expected/correct behavior is “return multiple ranked candidates + ask a clarifying question.” Short descriptions are the main driver of ambiguity, so this is a major gap.
- **NOT_FOUND behavior is mostly untested**: aside from `validation_invalid`, there are no known-absent cases for part/vendor/description/hierarchy lookups, so we haven’t validated “don’t guess” in common flows.
- **VMRS prefix questions aren’t tested**: questions always use full `xxx-xxx-xxx` codes (no prefix-only queries like `xxx-xxx`).

Minimal additions to close the short-description gap:
- Add a small set of **1-word** and **2-word** description questions with expected behavior = **AMBIGUOUS** (ranked candidates + clarifying question), chosen from generic/high-frequency terms in the vendor descriptions (e.g., `"FILTER"`, `"HOSE"`, `"SWITCH"`, `"SEAT BELT"`, `"FUEL GAUGE"`).
- Add a few short-description **normalization variants** (unquoted text, case differences, stripped punctuation, extra spaces) to confirm robust handling.

### How “pass/fail” was decided (plain English)

- **VMRS code lookups** (part/vendor/description questions): **pass** if the correct VMRS code appears in the assistant’s **top 3** VMRS codes mentioned in its final response.
- **Vendor-parts-from-VMRS** (`vendor_mapping`): **pass** if the assistant includes **at least one** part number that appears in the vendor CSV under that VMRS code (we do not require listing *all* parts).
- **Hierarchy questions**: **pass** if the requested VMRS code is present in the final response (with hierarchy text around it).
- **Comparison questions**: **pass** if the assistant’s YES/NO matches whether the two parts map to the **same VMRS code** in the vendor CSV.
- **Validation questions**:
  - `validation_valid`: **pass** if the assistant clearly says **YES**.
  - `validation_invalid`: **pass** only if the code is **absent from the vendor CSV** *and* the assistant answers **NO / NOT_FOUND**.

### Results (current)

- **73/80 pass**
- **All 80 tests have transcripts** (`full_conversation` populated).

| Category | Pass | Total |
|---|---:|---:|
| part_lookup | 10 | 10 |
| vendor_lookup | 9 | 10 |
| description_exact | 10 | 10 |
| description_partial | 9 | 10 |
| hierarchy_navigation | 10 | 10 |
| vendor_mapping | 10 | 10 |
| validation_valid | 5 | 5 |
| validation_invalid | 0 | 5 |
| comparison | 10 | 10 |

### Remaining failing test_ids (7)

- **VP-51dc6a**: vendor CSV contains `ZT-105-RONT|STELLANA → 017-005-002`, but the transcript returned **NOT_FOUND**.
- **DP-3dd466**: vendor CSV row is **“DRIVERS SIDE SEAT BELT”** (VMRS `002-011-003`), but the transcript interpreted the query as “seat assembly” and returned other seat-related codes.
- **VI-7befa4, VI-82290b, VI-1062e3, VI-503d29, VI-d62d5a**: these are labeled “invalid” because they do **not appear in the vendor mapping CSV**; however the Neo4j database contains them in the VMRS hierarchy and the assistant answered **valid**.

### Important note on `validation_invalid` (definition mismatch)

These 5 failures do **not** mean the system is “wrong about VMRS.” They mean our current *scoring oracle* is “present in vendor mappings” while the system is answering “present in VMRS hierarchy.” If we want “VMRS validity” to mean “exists in the hierarchy,” the `validation_invalid` tests (or their oracle) should be updated accordingly.

