# Interface Test Plan: VMRS Question Set

## Executive Summary (Current Run)

| Metric | Value |
|--------|-------|
| Total tests | 80 |
| Pass | 73 (91.25%) |
| Fail | 7 |
| True interface defects | 2 |
| Test-design issues | 5 (validation_invalid oracle mismatch) |

**Key findings**:
- Core lookup functionality (part, vendor, description, hierarchy, comparison) works well: 68/70 pass (97%)
- Vendor mapping queries work correctly: 10/10 pass
- Two true failures require investigation: VP-51dc6a (STELLANA part not found), DP-3dd466 (description partial matched wrong codes)
- Five validation_invalid "failures" are test-design issues, not interface defects (see "Note on VMRS validity definitions")

**Coverage gaps** (documented, not blocking for POC):
- No AMBIGUOUS behavior tests
- No NOT_FOUND tests for lookup categories
- No short-description (1-2 word) tests
- No VMRS prefix queries
- Stability testing not performed

## Objective
Validate that the stakeholder-facing interface (Claude Code with Neo4j MCP) returns correct VMRS codes, relationships, and vendor mappings for common user questions, and that it handles unknowns with a clear, user-friendly response.

## Audience
This plan is written for stakeholders who need confidence that the interface answers real-world questions accurately and consistently.

## Scope

We will test the interface using a predefined, loggable suite in `tests/test_questions/test_log.csv`.

Related (but not the executed suite):
- `tests/test_questions/questions.md` is a stakeholder prompt backlog / example set (useful for brainstorming patterns and future test expansion).

A stakeholder question is **in scope** if the answer can be derived **solely** from the current Neo4j snapshot’s fields and relationships covering:
- **Part identity**: part_id (if present), vendor/manufacturer part number
- **Part description**: description text fields stored on part/vendor-part nodes
- **Vendor/manufacturer**: vendor identity and vendor ↔ vendor-part relationships
- **VMRS**: VMRS codes and VMRS labels/descriptions stored in the graph
- **Relationships**:
  - VMRS hierarchy: System → Assembly → Component (PART_OF)
  - Vendor mapping: VendorPart → VMRS Component/Code (MAPS_TO)
  - Vendor ownership: Vendor → VendorPart (MANUFACTURES)

### Allowed Inputs (what stakeholders can ask with)
An in-scope question contains at least one of the following inputs:
- part_number (vendor/manufacturer part number)
- part_id (internal ID, if available in the snapshot)
- vendor/manufacturer name
- vmrs_code (full code or prefix)
- description text (free text)

Modifiers such as “with vendor X”, “compare A vs B”, “same VMRS code/component?”, “show hierarchy”, “list mapped vendor parts”, and “validate this code” are in scope.

### Fuzzy Matching Boundaries
- Description and vendor/manufacturer name queries may use partial text and tolerate minor typos.
- Exact identifiers (part_number, part_id, vmrs_code) are treated as exact unless the user explicitly requests a loose search.

### Ambiguity Triggers
- Same or near-identical descriptions mapping to multiple components or multiple vendors.
- VMRS code prefix matches that resolve to multiple codes.
- Part number appears under multiple vendors (when applicable).

### Required Response Types (Output Contract)
Every answer must be one of the following response types and include the required information for that type. The full transcript must include the tool traces/queries that support the result.

1) **RESOLVED** (single correct target identified)
- Return resolved VMRS code(s) and, when applicable, the full hierarchy path:
  - system {code, name} → assembly {code, name} → component {code, name}
- When vendor mapping is requested, return vendor mappings:
  - {vendor, vendor_part_number, vendor_part_description, mapped_vmrs_code/component}
- For scoring: expected answer must appear in ranked top 3 candidates (if multiple returned)

2) **AMBIGUOUS** (multiple plausible matches)
- Return a ranked candidate list (top 3 required, top 5 optional for display) with distinguishing attributes (code/name/description/vendor hints)
- Ranking priority: exact identifier match > exact phrase match > fuzzy match
- Ask a clarifying question needed to select the correct target
- For scoring: expected answer must appear in ranked top 3 candidates

3) **NOT_FOUND** (absent from the snapshot)
- Explicitly state “not found in the current snapshot”
- State what was searched (identifier/text) and what scope/fields were checked
- Provide a concrete next step (e.g., ask for vendor, partial part number, alternate description)
- Must not guess or fabricate VMRS codes or vendor mappings

4) **COMPARISON** (two+ items)
- Provide each item’s resolution status (RESOLVED/AMBIGUOUS/NOT_FOUND)
- State whether they map to the same VMRS code and/or same component (true/false/unknown)
- If applicable, state the relationship (parent/child/sibling/unrelated/unknown)

5) **VALIDATION** (VMRS code existence/validity)
- State whether the code exists in the snapshot (true/false)
- If it exists, include the code name/label and hierarchy path when available

## Test Set Composition
Counts are bounded and tracked per test_id in `tests/test_questions/test_log.csv` and the source of truth.

By category:
- part_lookup: 10
- vendor_lookup: 10
- description_exact: 10
- description_partial: 10
- hierarchy_navigation: 10
- vendor_mapping: 10
- validation_valid: 5
- validation_invalid: 5
- comparison: 10

Total: 80

Category values (as they appear in `tests/test_questions/test_log.csv`):
- part_lookup
- vendor_lookup
- description_exact
- description_partial
- hierarchy_navigation
- vendor_mapping
- validation_valid
- validation_invalid
- comparison

By behavior:
- KNOWN_PRESENT: 75
- KNOWN_ABSENT: 5
- AMBIGUOUS: 0 (gap—see "Known Coverage Gaps" below)

## Known Coverage Gaps

The current 80-question suite does not cover the following scenarios. These gaps are documented for future expansion and are not blocking for the current POC validation.

### 1. AMBIGUOUS behavior (0 tests)
No questions where the expected response is "return ranked candidates + ask clarifying question." The plan defines AMBIGUOUS as a required response type (see "Required Response Types"), but no test cases exercise it.

**Why it matters**: Short or generic descriptions (1-2 words like "FILTER", "HOSE", "SWITCH") commonly produce multiple plausible matches. Without AMBIGUOUS tests, we cannot validate the system's ranking logic or clarifying-question behavior.

**Recommended addition**: Add 5-10 short-description questions with `expected_behavior = AMBIGUOUS` and verify the correct answer appears in the top-3 ranked candidates.

### 2. NOT_FOUND for lookup categories (0 tests)
No part_lookup, vendor_lookup, description_exact, description_partial, or hierarchy_navigation tests with `expected_behavior = KNOWN_ABSENT`. Only validation_invalid tests absent scenarios (and those have a definitional conflict—see note below).

**Why it matters**: The plan requires NOT_FOUND responses to state what was searched, what scope was checked, and provide a concrete next step. Without KNOWN_ABSENT lookup tests, we cannot validate "don't guess" behavior in common flows.

**Recommended addition**: Add 5-10 lookup questions using fabricated part numbers, nonexistent vendor names, or descriptions that do not appear in the vendor data.

### 3. Short descriptions (0 tests)
The description_partial category explicitly filters to descriptions with 3+ words and only removes the final word. This means 1-word and 2-word description lookups are structurally excluded.

**Why it matters**: Short descriptions are common in real usage and typically produce the most ambiguity. They are also where fuzzy matching and synonym handling are most likely to surface issues.

**Recommended addition**: Add a `description_short` category with 1-2 word queries (e.g., "FILTER", "SEAT BELT", "FUEL GAUGE") and appropriate expected_behavior (likely AMBIGUOUS for generic terms, RESOLVED for specific terms).

### 4. VMRS prefix queries (0 tests)
All validation and hierarchy questions use full xxx-xxx-xxx codes. Partial codes like "042-002" (system-assembly only) or "042" (system only) are untested.

**Why it matters**: Users may ask about VMRS prefixes when they don't know the full component code. The system should either resolve to the prefix node or clarify which component is intended.

**Recommended addition**: Add 3-5 prefix queries to hierarchy_navigation or validation categories.

### 5. Phrasing variations (0 tests)
All questions use exact templates (e.g., "What is the VMRS code for part number X?"). Alternate phrasings, typos, case variations, missing quotes, and synonyms are untested.

**Why it matters**: Real users will not use exact template phrasing. Robustness to minor variations is important for production readiness but is out of scope for this POC.

**Recommendation**: Document as a future test expansion; not required for current POC sign-off.

### 6. Multi-turn conversations (0 tests)
Each test is a single question with a single answer. Follow-up questions, clarifications after AMBIGUOUS responses, and conversational context are untested.

**Why it matters**: The AMBIGUOUS response type is designed to prompt clarifying questions, but we never test what happens when the user answers them.

**Recommendation**: Defer to a future "conversation flow" test suite.

## How the test questions were generated (source of truth)

The current 80-question suite in `tests/test_questions/test_log.csv` was generated from vendor mapping data using the process described in:
- `tests/test_questions/plans/generate_test_questions_plan.md`

In brief:
- **Source data**: `vendor data/checked/Motors Part Cleanup - Return Data.csv`
- **Row key**: `{PART}|{MANUFACTURER}` (used for traceability and stable IDs)
- **Stable test IDs**: `{PREFIX}-{HASH6}`, where `HASH6` is the first 6 hex chars of SHA256(row_key)
- **Question templates**: the 9 categories in the plan (10 each, except validation 5/5) totaling 80
- **Source-of-truth fields**: `expected_answer` and `vendor_parts` are derived from the vendor CSV (not directly from the VMRS handbook)

## Interface Under Test
- Primary interface: Claude Code using the Neo4j MCP server (https://github.com/neo4j-contrib/mcp-neo4j).
- Prompt context: `interface prompts/lookup_agent/main_v2.txt`, `interface prompts/lookup_agent/neo4j_schema.txt`, `interface prompts/lookup_agent/priority_sites.txt`.
- Web search is disabled for this test plan, even if the prompt context allows it.
- Claude Code build: record from the Claude "About" screen (current run used the build available on 1/13/2026).
- Model: Sonnet 4.5.
- Neo4j MCP version: v0.8.2.
- Environment: Claude Code connected to Neo4j via MCP.

## Out of Scope
- Data quality auditing and ETL/ingestion verification (duplicates/orphans/coverage/completeness checks)
- Model training or fine-tuning evaluation
- Load, latency, or scalability testing
- Neo4j acceptance tests beyond the interface surface
- Questions requiring information not represented in the snapshot (e.g., pricing, inventory, lead times, recommendations like “best vendor”)

## Test Assets
- Executed test suite (questions + expected answers + scoring fields): `tests/test_questions/test_log.csv`
- Evidence (full transcripts): `tests/test_questions/conversations/<test_id>.md`
- Stakeholder-readable summary: `tests/test_questions/EVALUATION_SUMMARY.md`
- Source-of-truth inputs for generating expected answers:
  - `vendor data/checked/Motors Part Cleanup - Return Data.csv`
  - (source spreadsheet): `vendor data/checked/Motors Part Cleanup - Return Data.xlsx`
- Source-of-truth rule (current state): Every test row in `test_log.csv` must have:
  - `test_id`
  - `question_text`
  - `expected_behavior`
  - `expected_answer` (for KNOWN_PRESENT)
- Related prompt backlog (not the executed suite): `tests/test_questions/questions.md`
- Prompt context sources: `interface prompts/lookup_agent/main_v2.txt`, `interface prompts/lookup_agent/neo4j_schema.txt`, `interface prompts/lookup_agent/priority_sites.txt`
- Ground truth vendor data: `vendor data/checked/` (source of truth for vendor mappings and part data)
- Reference sources: VMRS handbook content and the current graph/data snapshot used by the interface

### What was actually used in the current run (Claude subagent + hook)

This run was executed via a Claude subagent plus a SubagentStop hook.

- **Subagent**: `.claude/agents/vmrs-test-runner.md`
  - Invoked with prompts that include a stable test ID prefix like:
    - `[TEST_ID: PN-18ba5e] What is the VMRS code for part number 2234788PE?`
- **Hook**: `.claude/hooks/save_vmrs_result.py` (wired via `.claude/settings.json`)
  - On SubagentStop, it:
    - Parses the subagent transcript to extract `test_id` from the `[TEST_ID: ...]` tag.
    - Writes the full conversation (user prompt, tool calls/results, assistant answer) to:
      - `tests/test_questions/conversations/<test_id>.md`
    - Updates `tests/test_questions/test_log.csv` by setting the `full_conversation` column to the relative path:
      - `tests/test_questions/conversations/<test_id>.md`

### Test suite source-of-truth files (what to look at)

- **Test cases + scoring fields**: `tests/test_questions/test_log.csv`
- **Stakeholder-readable run summary**: `tests/test_questions/EVALUATION_SUMMARY.md`
- **Evidence (tool calls + query results + final answers)**: `tests/test_questions/conversations/<test_id>.md`
- **Prompt backlog / examples**: `tests/test_questions/questions.md`

### Source-of-truth fields (current suite)

In the current run, the “source of truth” for each test is stored directly in `tests/test_questions/test_log.csv`:
- `expected_answer`: expected VMRS code (or, for comparison, a semicolon-delimited pair of VMRS codes)
- `vendor_parts`: for vendor-mapping tests, the expected vendor-part set/size indicator (current format is a lightweight summary like `n=118`)

Optional/future enhancement:
- Store richer expected hierarchy fields (system/assembly/component names) in a dedicated expected-answers artifact, or extend the CSV schema.

## Execution Approach (end-to-end)

### Claude subagent + hook (current run)

1. **Prepare the suite**
   - Ensure `tests/test_questions/test_log.csv` contains the full question set with stable `test_id`s, `category`, and `expected_answer` populated.
   - Ensure the prompt context files are up to date:
     - `interface prompts/lookup_agent/main_v2.txt`
     - `interface prompts/lookup_agent/neo4j_schema.txt`
     - `interface prompts/lookup_agent/priority_sites.txt`
2. **Execute each test**
   - For each row in `test_log.csv`, ask the subagent `.claude/agents/vmrs-test-runner.md` the question in `question_text` with the required prefix:
     - `[TEST_ID: <test_id>] <question_text>`
3. **Capture evidence (automatic)**
   - On SubagentStop, `.claude/hooks/save_vmrs_result.py` writes:
     - `tests/test_questions/conversations/<test_id>.md`
   - And updates `tests/test_questions/test_log.csv`:
     - sets `full_conversation` to `tests/test_questions/conversations/<test_id>.md`
4. **Score + label outcomes**
   - Update `pass_fail` (pass/fail) and `failure_type` where needed.
   - Use the pass/fail rules in this document (top-3 candidate rule, vendor-mapping rule, etc.).
5. **Summarize**
   - Update `tests/test_questions/EVALUATION_SUMMARY.md` with totals, category breakdown, and the short list of notable failures + why.

## Ad Hoc Execution (Hook-Based)

Mode A (Claude subagent + hook) is the primary execution path used in the current run; this section is retained as a quick reference.

### Setup
- Hook config: `.claude/settings.json` (SubagentStop hook for `vmrs-test-runner`)
- Hook script: `.claude/hooks/save_vmrs_result.py`
- Output: `tests/test_questions/test_log.csv` (`full_conversation` column)
- Transcripts: `tests/test_questions/conversations/<test_id>.md` (written by the hook)

### Usage
Include the test_id in the prompt when invoking the subagent:
```
[TEST_ID: PN-18ba5e] What is the VMRS code for part number 2234788PE?
```

The hook automatically:
1. Parses the test_id from the prompt
2. Captures the full conversation (user prompt, tool calls, assistant response)
3. Updates the matching row in `test_log.csv`

### Prompt Format
```
[TEST_ID: <test_id>] <question_text>
```

The test_id pattern is `XX-XXXXXX` (category prefix + hex suffix), e.g., `PN-18ba5e`, `VP-666da5`, `DE-c563a9`.

## Test Log Schema
Current run log schema (matches `tests/test_questions/test_log.csv`):
- test_id
- category
- expected_behavior: KNOWN_PRESENT | KNOWN_ABSENT | AMBIGUOUS
- question_text
- row_key
- expected_answer
- vendor_parts
- pass_fail
- failure_type
- full_conversation (relative path to `tests/test_questions/conversations/<test_id>.md`)

## Pass/Fail Criteria
- Baseline coverage: 100% of rows in `tests/test_questions/test_log.csv` return correct results or a clear, accurate "not found" response.
- **Correct if in top 3**: For VMRS-code lookup questions, a response is correct if the expected VMRS code appears in the top 3 ranked candidates (for RESOLVED or AMBIGUOUS responses).
- **Hierarchy consistency**: The returned system/assembly/component must match the VMRS code's PART_OF relationships in the graph (code prefix consistency).
- Any incorrect answer is a fail. No answer is a fail when the expected item exists in the source of truth.
- No critical defects:
  - Incorrect VMRS code for a known item (not in top 3)
  - Incorrect hierarchy (system/assembly/component) for a known item
  - **Hierarchy mismatch**: Expected VMRS code returned but with wrong assembly/system (VMRS prefix mismatch or PART_OF relationship inconsistency)
  - Incorrect vendor mapping for a known part
  - Interface errors that block completion of a question
  - Missing evidence: transcript does not include tool traces/queries for a test that used tools

### Per-category scoring notes (current suite)

- **part_lookup / vendor_lookup / description_exact / description_partial**:
  - pass if expected VMRS code appears in the assistant’s top 3 VMRS codes
- **vendor_mapping**:
  - pass if the assistant includes at least one vendor part number that exists under that VMRS code in the vendor mapping source of truth
- **hierarchy_navigation**:
  - pass if the requested VMRS code appears in the response (with hierarchy context around it)
- **comparison**:
  - pass if the YES/NO matches whether the two parts map to the same VMRS code in the vendor mapping source of truth
- **validation_valid / validation_invalid**:
  - see “validation_invalid definition” note below

### Acceptance for special behaviors
- **KNOWN_ABSENT**: must return NOT_FOUND behavior (no guessing) and a concrete next step.
- **AMBIGUOUS**: must return AMBIGUOUS behavior (ranked candidates and/or clarifying question); must not select a single answer without qualification.

### Note on VMRS validity definitions (source-of-truth conflict)

There are two common "valid VMRS" definitions:
- **Vendor-mapping validity** (what the current suite's oracle uses): "the code appears in the vendor mapping source of truth"
- **Hierarchy validity** (what the interface answers): "the code exists in the VMRS hierarchy in the Neo4j snapshot"

The current suite's `validation_invalid` cases are constructed as "not present in vendor mapping data," which conflicts with hierarchy existence. The interface correctly answers "valid" (exists in hierarchy) while the test oracle expects "invalid" (not in vendor mappings).

**Result**: All 5 validation_invalid tests fail, but these are **not true interface defects**. The interface is answering the question as a user would expect ("Does this VMRS code exist?"), not as the test oracle defines it ("Does this VMRS code have vendor mappings?").

**Resolution options**:
1. **Reclassify as PASS**: Accept that hierarchy validity is the correct interpretation and mark these tests as passing.
2. **Change the question**: Rephrase validation_invalid questions to "Do any vendor parts map to VMRS code X?" to match the oracle's definition.
3. **Replace test cases**: Generate new validation_invalid cases using VMRS codes that do not exist in the hierarchy (e.g., malformed codes like 999-999-999).

**Current status**: These 5 tests are counted as failures in the test log but are flagged as a test-design issue, not an interface defect.

## Stability Check (Nondeterminism)
- Run each test 2–3 times, especially description-based or ambiguous categories.
- Deterministic categories (exact part numbers / exact VMRS codes) must match 100%.
- Description-based categories must be consistent or return the same candidate set with the same top result.
- Record each run as a separate log row with the `attempt` field incremented.

**Current run status**: The suite was executed once only. Stability sampling (repeated runs) was **not performed** for this POC. The test log has no `attempt` column.

**Recommendation**: Stability testing is optional for POC sign-off but recommended before production deployment, especially for description-based categories where LLM nondeterminism may affect results.

## Risks and Assumptions
- The interface and the reference snapshot stay in sync for the duration of testing.
- Some failures may reflect vendor data gaps rather than interface defects; classify as DATA_GAP only when the source-of-truth/reference confirms missing/incorrect source data.
- Description-based matching depends on current search/synonym logic; document false positives and ambiguous results.

## Regression Policy
Re-run the full suite or a defined smoke subset when any of the following change:
- Prompt files in `interface prompts/`
- Schema mapping
- `vendor data/checked/` files
- Graph snapshot
- Neo4j MCP version
- Model ID or Claude Code build

## Roles and Ownership
- Test execution: Thupten
- Review and sign-off: Manager

## Reporting
Provide a concise results summary with:
- Pass/fail counts by category
- Notable failures with root cause notes (DATA_GAP vs interface behavior)
- Representative transcript excerpts for stakeholder review (linked from evidence)

## Result Review
- Test cases and responses are logged during execution; detailed review happens after the full run is complete.

## Next Steps
- Freeze `tests/test_questions/questions.md` and assign stable `test_id`s.
- Optional: create a dedicated expected-answers artifact (e.g., `tests/test_questions/expected_answers.json`) if you want the source of truth separated from `test_log.csv`.
- Run a pilot set (3–5 questions) to validate workflow and adjust categories/expectations.
- Execute the full suite, fix defects, and re-run failures until clean.
- Schedule stakeholder review and share the results summary with links to evidence.
