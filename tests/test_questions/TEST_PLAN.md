# Interface Test Plan: VMRS Question Set

## Objective
Validate that the stakeholder-facing interface (Claude Code with Neo4j MCP) returns correct VMRS codes, relationships, and vendor mappings for common user questions, and that it handles unknowns with a clear, user-friendly response.

## Audience
This plan is written for stakeholders who need confidence that the interface answers real-world questions accurately and consistently.

## Scope

We will test the interface against the stakeholder question set in `tests/test_questions/questions.md`.

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

2) **AMBIGUOUS** (multiple plausible matches)
- Return a ranked candidate list (top 5) with distinguishing attributes (code/name/description/vendor hints)
- Ranking priority: exact identifier match > exact phrase match > fuzzy match
- Ask a clarifying question needed to select the correct target

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
Counts are bounded and tracked per test_id in `tests/test_questions/questions.md` and the oracle.

By category:
- part_number exact: TK
- vendor + part_number: TK
- description exact: TK
- description partial/typo: TK
- hierarchy navigation: TK
- vendor mapping from VMRS: TK
- validation: TK
- comparison: TK

By behavior:
- KNOWN_PRESENT: TK
- KNOWN_ABSENT: TK
- AMBIGUOUS: TK

## Interface Under Test
- Primary interface: Claude Code using the Neo4j MCP server (https://github.com/neo4j-contrib/mcp-neo4j).
- Prompt context: `interface prompts/v2.txt`, `interface prompts/neo4j_schema.txt`, `interface prompts/priority_sites.txt`.
- Web search is disabled for this test plan, even if the prompt context allows it.
- Claude Code build: record from Claude "About" screen in the run manifest; target run uses the build available on 1/13/2026.
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
- Primary question list: `tests/test_questions/questions.md` (stakeholder-driven questions)
- Expected answers (oracle): `tests/test_questions/expected_answers.json` (or `.csv`) keyed by `test_id`
- Expected answers source: `vendor data/checked/Motors Part Cleanup - Return Data.xlsx` (input source used to build the oracle)
- Oracle-backed rule: Every generated question must map to a `test_id` with an `expected_answer` in `expected_answers.*`. If an expected answer cannot be derived, the test must be labeled KNOWN_ABSENT with an expected NOT_FOUND response.
- Generated questions should follow the same patterns and style as the examples in `tests/test_questions/questions.md`.
- Prompt context sources: `interface prompts/v2.txt`, `interface prompts/neo4j_schema.txt`, `interface prompts/priority_sites.txt`
- Ground truth vendor data: `vendor data/checked/` (source of truth for vendor mappings and part data)
- Reference sources: VMRS handbook content and the current graph/data snapshot used by the interface
- MCP harness: `mcp/test_questions_mcp.py` (runs the suite and writes logs/transcripts)
- Run manifest template: `tests/test_questions/runs/manifest_template.json` (copy to `tests/test_questions/runs/<run_id>/manifest.json`)

## Execution Approach
1. Create a `run_id` and `manifest_id`, then write a run manifest at `tests/test_questions/runs/<run_id>/manifest.json` capturing:
   - Claude Code build (from "About"), model ID, Neo4j MCP version
   - Prompt file hashes (v2.txt, neo4j_schema.txt, priority_sites.txt)
   - Neo4j snapshot identifier (dump name/commit/date) and snapshot date
   - Any relevant runtime configuration (e.g., temperature if configurable)
2. Run each question through the interface and capture a complete transcript that includes:
   - Full final answer text
   - Prompt context used for the run
   - MCP/tool calls and outputs
   - Cypher queries/results (or equivalent returned records)
   - Any intermediate outputs produced by the interface
   - Save each transcript under `tests/test_questions/runs/<run_id>/transcripts/<test_id>_attempt<k>.txt`
3. Verify each response against the oracle (`expected_answers.*`) and reference sources; log pass/fail with a short note.
4. Re-run failed tests after fixes and confirm resolution.

## Test Log Schema
Per-question log rows are intentionally slim, with run-level context captured in the run manifest:
- run_id
- manifest_id
- test_id
- attempt (1..N for stability runs)
- question_text
- category (description lookup, part lookup, comparison, vendor mapping, vendor lookup, validation, hierarchy navigation)
- expected_behavior: KNOWN_PRESENT | KNOWN_ABSENT | AMBIGUOUS
- expected_answer (string or JSON)
- actual_answer (full final response text)
- pass_fail
- failure_type: DATA_GAP | PROMPT | QUERY_LOGIC | FUZZY_MATCH | HALLUCINATION | TOOL_ERROR
- evidence_link (full transcript path under `tests/test_questions/runs/<run_id>/`; includes prompt context, MCP/tool calls, Cypher queries/results, intermediate outputs, and final answer)

## Pass/Fail Criteria
- Baseline coverage: 100% of questions in `tests/test_questions/questions.md` return correct results or a clear, accurate “not found” response.
- Any incorrect answer is a fail. No answer is a fail when the expected item exists in the oracle/ground truth.
- No critical defects:
  - Incorrect VMRS code for a known item
  - Incorrect hierarchy (system/assembly/component) for a known item
  - Incorrect vendor mapping for a known part
  - Interface errors that block completion of a question
  - Missing evidence: transcript does not include tool traces/queries for a test that used tools

### Acceptance for special behaviors
- **KNOWN_ABSENT**: must return NOT_FOUND behavior (no guessing) and a concrete next step.
- **AMBIGUOUS**: must return AMBIGUOUS behavior (ranked candidates and/or clarifying question); must not select a single answer without qualification.

## Stability Check (Nondeterminism)
- Run each test 2–3 times, especially description-based or ambiguous categories.
- Deterministic categories (exact part numbers / exact VMRS codes) must match 100%.
- Description-based categories must be consistent or return the same candidate set with the same top result.
- Record each run as a separate log row with the `attempt` field incremented.

## Risks and Assumptions
- The interface and the reference snapshot stay in sync for the duration of testing.
- Some failures may reflect vendor data gaps rather than interface defects; classify as DATA_GAP only when the oracle/reference confirms missing/incorrect source data.
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
- Build `tests/test_questions/expected_answers.json` (oracle) from `Motors Part Cleanup - Return Data.xlsx` and VMRS handbook references.
- Implement `mcp/test_questions_mcp.py` to run the suite and write `manifest.json`, transcripts, and the per-question log.
- Run a pilot set (3–5 questions) to validate workflow and adjust categories/expectations.
- Execute the full suite, fix defects, and re-run failures until clean.
- Schedule stakeholder review and share the results summary with links to evidence.
