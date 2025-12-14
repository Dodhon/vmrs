---
name: Stakeholder chatbot test plan
overview: Create a minimal, stakeholder-facing test plan for demonstrating Claude Desktop (Neo4j MCP) answering VMRS + vendor-part questions, backed by your existing Neo4j dataset and acceptance artifacts. Includes a short demo script, an edge-case matrix, pass/fail criteria, and a fallback plan.
todos:
  - id: prep-demo-qs
    content: Select 5–6 stakeholder-friendly demo questions (Q1–Q6) and verify they succeed live in Claude Desktop + Neo4j MCP; capture Cypher + outputs for each.
    status: pending
  - id: prompt-bakeoff
    content: Run a small prompt bakeoff (v2 vs 2 variants) on a fixed question set; pick the prompt with best correctness + best stakeholder UX (clarifying questions instead of guessing, concise answers).
    status: pending
  - id: run-mini-regression
    content: Run a small pre-meeting regression (e.g., 15 questions) sampled from tests/neo4j_acceptance/questions.json covering typos, ambiguity, and multiple systems; record pass/fail and queries.
    status: pending
    dependencies:
      - prep-demo-qs
      - prompt-bakeoff
  - id: vendor-demo-check
    content: Decide whether to include VendorPart mapping in the meeting; if yes, verify VendorPart nodes + MAPS_TO + MANUFACTURES exist (per scripts/refactor_vendor_schema.py) and pick 1–2 PoC examples.
    status: pending
    dependencies:
      - prep-demo-qs
  - id: fallback-pack
    content: Create a fallback “screenshots/answers” pack for the demo questions (answers + Cypher + outputs) in case live querying fails.
    status: pending
    dependencies:
      - prep-demo-qs
  - id: create-github-issue
    content: Create a GitHub issue containing the stress-test matrix, acceptance criteria, and known gaps (from tests/neo4j_acceptance/summary_report.txt).
    status: pending
    dependencies:
      - run-mini-regression
---

# Stakeholder Test Plan (Claude Desktop + Neo4j MCP)

## Goals (what we’re proving)
- **Non-technical user value**: stakeholder can ask plain-English questions and get **correct VMRS codes + context** (system/assembly/component) and, when available, **vendor part mappings**.
- **Trust & traceability**: every answer can be traced to **(a) the Neo4j query used** and **(b) the underlying dataset snapshot**.
- **Known limits upfront**: we can show “not found” cases safely and explain why (missing codes in snapshot), based on prior QA.

## Scope (minimal)
- **In scope**: Q&A via Claude Desktop using the Neo4j MCP against the current graph (VMRS hierarchy + vendor parts if loaded).
- **Out of scope**: chatbot UI/infra, training workflows, LLM extraction quality beyond what’s already loaded.

## What to validate (acceptance criteria)
- **Correctness**:
  - Returns the **right VMRS code** for common part descriptions.
  - Returns the **right hierarchy context** via `PART_OF` (Component → Assembly → System).
  - For vendor parts: returns the correct **VendorPart → Component (`MAPS_TO`)** mapping when present.
- **Behavior under ambiguity**:
  - If the question is underspecified (e.g., “seal”, “bracket”), the agent returns **top candidates + asks a clarifying question** (instead of guessing silently).
- **“Not found” behavior**:
  - If no match exists in the snapshot, the agent says **not found** and offers the **closest alternatives** (e.g., broader assembly-level items) or asks for more detail.
- **Efficiency** (for meeting): typically **≤2 Cypher queries** and **fast response**.

## Prompt testing (optimize Claude Desktop system prompt)
You said you’re using the prompts under [`interface prompts/`](/Users/thuptenwangpo/Documents/GitHub/vrms/interface%20prompts) and **`v2.txt` is the current baseline**.\n+
### Why test prompts at all?
- The system prompt directly affects whether the agent:\n+  - asks clarifying questions vs guessing\n+  - searches `Component` vs `VendorPart`\n+  - shows Cypher (good for traceability, bad for non-technical UX)\n+  - wastes time fetching “schema first” every time\n+
### Bakeoff setup (minimal)
- **Question set (15 total)**: sample from [`tests/neo4j_acceptance/questions.json`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/questions.json)\n+  - 5 clean “happy path” (specific part names)\n+  - 5 typos/messy text (e.g., “winshield”, “mirrior”)\n+  - 5 ambiguous (e.g., “seal”, “bracket”, “switch”)\n+- **Scoring**:\n+  - **Correctness**: correct code returned (or correct “not found”) vs expected\n+  - **UX**: did it ask a clarifying question when ambiguous?\n+  - **Efficiency**: number of Neo4j queries (aim ≤2)\n+  - **Answer quality**: concise + includes system/assembly context\n+
### Prompts to compare (start minimal: 3)
- **Prompt A (baseline)**: current [`interface prompts/v2.txt`](/Users/thuptenwangpo/Documents/GitHub/vrms/interface%20prompts/v2.txt)\n+- **Prompt B (stakeholder-optimized)**: same as v2 but:\n+  - **No web search fallback** (Neo4j-only for the meeting)\n+  - **Don’t fetch schema first by default** (only if a query fails)\n+  - **Hide Cypher by default**; offer “I can show the query if you want”\n+  - Return **1 best answer** unless ambiguous; if ambiguous, ask 1 question or show top 3\n+- **Prompt C (debug/dev)**: same as Prompt B but **always include the Cypher** (useful when you’re validating correctness pre-meeting)\n+
### Expected outcome
- Use **Prompt B** in the stakeholder meeting (best UX), and keep **Prompt C** for pre-meeting validation.

## Pre-meeting readiness checklist (live demo)
- **Graph is built & consistent**
  - VMRS hierarchy import path: [`scripts/import_csv_to_neo4j.py`](/Users/thuptenwangpo/Documents/GitHub/vrms/scripts/import_csv_to_neo4j.py) using [`src/neo4j_client.py`](/Users/thuptenwangpo/Documents/GitHub/vrms/src/neo4j_client.py).
  - VendorPart schema path (if you want vendor demo): [`scripts/refactor_vendor_schema.py`](/Users/thuptenwangpo/Documents/GitHub/vrms/scripts/refactor_vendor_schema.py).
  - Target shape/counts are described in [`docs/NEO4J_BUILD_GUIDE.md`](/Users/thuptenwangpo/Documents/GitHub/vrms/docs/NEO4J_BUILD_GUIDE.md).
- **Known QA baseline**
  - Existing acceptance questions live in [`tests/neo4j_acceptance/questions.json`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/questions.json).
  - Prior run summary (includes known missing codes) is in [`tests/neo4j_acceptance/summary_report.txt`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/summary_report.txt).

## Stakeholder-facing demo script (7 minutes, minimal)
Use these as the *exact* user questions you type into Claude Desktop. Each should show: the answer + a short explanation + (optionally) the Cypher the agent ran.

### Part → VMRS code (happy path)
- **Q1**: “What is the VMRS code for a mirror actuator?”
  - Grounded in your existing template prompt: [`prompts/test_case_prompt.txt`](/Users/thuptenwangpo/Documents/GitHub/vrms/prompts/test_case_prompt.txt) and prior results: [`tests/neo4j_acceptance/results.txt`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/results.txt).
- **Q2**: “What is the VMRS code for an A/C receiver dryer?”
- **Q3**: “What is the VMRS code for blower motor?” (from your acceptance set)

### Show hierarchy context (why the code is trustworthy)
- **Follow-up** (after any of Q1–Q3): “What system and assembly does that belong to?”
  - Expect: `Component` + parent `Assembly` + parent `System` via `PART_OF`.

### Vendor part mapping (only if VendorPart nodes are loaded)
Pick one example from your PoC subsets:
- **Q4**: “For VMRS `044-002-087` (fuel/water separator filter), show vendor parts and manufacturers.”
  - Use the PoC context in [`docs/analysis/POC_READY_SUBSETS.md`](/Users/thuptenwangpo/Documents/GitHub/vrms/docs/analysis/POC_READY_SUBSETS.md).

### Demonstrate safety on ambiguity (don’t guess)
- **Q5**: “What’s the VMRS code for a bracket?”
  - Expected behavior: ask clarifying question or return top-N candidates with system/assembly context.

### Demonstrate “not found” gracefully (pre-briefed limitation)
- **Q6**: Ask one of the known missing codes from the summary (so you control the narrative):
  - Example: “What is the VMRS code for vent, cab exhaust?” (listed as missing in the prior summary)
  - Expected behavior: “Not found in this snapshot” + nearest alternative suggestions.

## Stress-test matrix (what could break it)
Use this as your *ad hoc* test checklist. You don’t need to run all of it in the meeting; run it beforehand and keep results as backup.

- **Typos / messy text**: misspellings like those in [`tests/neo4j_acceptance/questions.json`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/questions.json) (e.g., “winshield”, “mirrior”, “strator”).
- **Synonyms**: “dryer” vs “drier”, “A/C” vs “air conditioning”, “cab” vs “sleeper”.
- **Underspecified terms**: “seal”, “switch”, “insert”, “control arm” (should clarify).
- **Pluralization & casing**: “filters” vs “filter”, “BLOWER MOTOR” vs “blower motor”.
- **Code input**:
  - Exact code lookup (`044-001-001`) should return the component and its path.
  - Invalid format (`44-1-1`) should be rejected or corrected.
- **VendorPart edge cases** (if enabled):
  - Multiple VendorParts mapping to same Component.
  - VendorPart with missing VMRS (`vmrs` empty/`nan`) should be reported as unclassified.

## How to run acceptance quickly (pre-meeting)
- Start from the existing 50-question suite in [`tests/neo4j_acceptance/questions.json`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/questions.json).
- For each question, record:
  - The user question
  - The Cypher used (Claude Desktop MCP output)
  - The returned `(code, name)` and hierarchy
  - Pass/fail vs expected
- Use the existing query patterns in [`tests/neo4j_acceptance/queries.json`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/queries.json) as a playbook for consistent searching.

## Ad hoc codebase review (what matters for this demo)
- **VMRS hierarchy correctness**:
  - Built from CSV via [`scripts/import_csv_to_neo4j.py`](/Users/thuptenwangpo/Documents/GitHub/vrms/scripts/import_csv_to_neo4j.py) using deterministic code parsing and relationship fixing in [`src/neo4j_client.py`](/Users/thuptenwangpo/Documents/GitHub/vrms/src/neo4j_client.py).
- **Vendor mapping correctness** (if used in demo):
  - Vendor parts are their own nodes, linked via `(:VendorPart)-[:MAPS_TO]->(:Component)` in [`scripts/refactor_vendor_schema.py`](/Users/thuptenwangpo/Documents/GitHub/vrms/scripts/refactor_vendor_schema.py).
- **Known data gaps**:
  - Prior acceptance indicates a small set of “not found” codes and some fuzzy-description issues: [`tests/neo4j_acceptance/summary_report.txt`](/Users/thuptenwangpo/Documents/GitHub/vrms/tests/neo4j_acceptance/summary_report.txt).

## Meeting fallback plan (if anything goes sideways)
- Keep a backup doc with:
  - The demo questions (Q1–Q6)
  - The last-known-good answers
  - The Cypher used and the output
- If a live question fails:
  - Acknowledge “not in snapshot / needs disambiguation”, and pivot to a nearby successful query (e.g., ask for more context or show hierarchy traversal from a known code).

## Deliverables to prepare (minimal)
- A 1-page “Demo Script + Expected Outputs” (copy/paste into your notes).
- A “Stress-test results” table (even 15–20 rows is enough) capturing queries + outputs.
- A GitHub issue titled “Stakeholder stress-test plan (Claude Desktop + Neo4j MCP)” with the matrix above and the known gaps list.
