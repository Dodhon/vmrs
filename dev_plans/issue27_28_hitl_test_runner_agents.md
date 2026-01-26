# Plan: HITL Test Runner Sub-Agents (Issues #27, #28)

## Links
- Issue #27: Add test runner agent for HITL capture MCP server (`mcp/hitl_get_feedback`)
- Issue #28: Add test runner agent for HITL review MCP server (`mcp/hitl_review`)

Key reference prompts (user-facing behavior):
- VMRS lookup agent prompt: `interface prompts/lookup_agent/main_v4.txt`
- HITL review agent prompt: `interface prompts/hitl_review_agent/main_v3.txt`

Existing runners:
- Neo4j QA runner: `.claude/agents/vmrs-test-runner.md`

MCP servers:
- Capture server: `mcp/hitl_get_feedback/server.py`
- Review server: `mcp/hitl_review/server.py`

## Goal
Add test runner sub-agents (similar to `vmrs-test-runner`) that match the **real product architecture**:

**User-facing agents**
1) **VMRS lookup agent**: answers using Neo4j (and optional web fallback) and captures operator feedback into HITL when present.
2) **HITL review agent**: helps a different operator approve/reject pending HITL submissions.

**Test runner end state**
- `vmrs-test-runner` (Neo4j-only question answering)
- `vmrs-lookup-hitl-runner` (integration runner: lookup + HITL capture)
- `hitl-review-runner` (review operator workflow)

Optional (lower-level smoke test; not a user-facing agent):
- `hitl-capture-runner` (exercise capture MCP tools directly)


## Non-goals
- Changing HITL schema or storage layout (tracked separately)
- Changing the capture/review MCP servers beyond what is required to run tests

## Design

### Architecture (ASCII)

User-facing agents:

```
Operator A
  |
  | (asks VMRS question + provides feedback)
  v
VMRS Lookup Agent
  |  \
  |   \  (when feedback present)
  |    \-> HITL Capture MCP (mcp/hitl_get_feedback)
  |          writes: HitL_local/pending/<id>.json
  v
Neo4j MCP (read-only) + optional web fallback
```

Review workflow:

```
Operator B (reviewer)
  |
  v
HITL Review Agent
  |
  v
HITL Review MCP (mcp/hitl_review)
  |
  +--> reads:  HitL_local/pending/<id>.json
  |
  +--> writes: HitL_local/reviewed/approved/<id>.json
  |            HitL_local/reviewed/rejected/<id>.json
```

Test runners (Claude Code subagents) mirror these surfaces:

```
vmrs-test-runner            (Neo4j-only Q&A)
vmrs-lookup-hitl-runner     (lookup + capture integration)
hitl-review-runner          (review approve/reject)
[optional] hitl-capture-runner (capture MCP smoke test)
```


### Repo recon requirement (process)
Before implementing a new runner or writing its plan, first scan:
- `README.md`
- relevant `dev_plans/`
- the MCP servers under `mcp/`
- existing `.claude/agents/`

This keeps runners aligned with established conventions.

### Sub-agent details (what each runner is for)

#### `vmrs-test-runner` (existing)
- **File:** `.claude/agents/vmrs-test-runner.md`
- **Purpose:** Neo4j-only VMRS Q&A (no HITL writes)
- **Tools:** Neo4j schema + cypher read
- **Use when:** validating retrieval/matching quality against question sets

#### `vmrs-lookup-hitl-runner` (new; integration runner)
- **File:** `.claude/agents/vmrs-lookup-hitl-runner.md`
- **Purpose:** exercises the *real lookup pipeline*: answer the question, then capture operator feedback into HITL when present
- **Tools:** Neo4j tools + HITL capture tools
- **Use when:** validating that your lookup agent correctly triggers HITL submissions with required submitter metadata

#### `hitl-review-runner`
- **File:** `.claude/agents/hitl-review-runner.md`
- **Purpose:** exercises the operator review workflow end-to-end
- **Tools:** HITL review MCP tools
- **Use when:** validating approve/reject decision recording + file movement

#### `hitl-capture-runner` (optional; MCP smoke test)
- **File:** `.claude/agents/hitl-capture-runner.md`
- **Purpose:** minimal direct exercise of the capture MCP server tools (submit + status/list)
- **Tools:** HITL capture MCP tools
- **Use when:** isolating capture MCP validation/storage behavior from lookup logic

### Agent locations
Sub-agent configs live under:
- `.claude/agents/`

### Tool wiring
The runners should call MCP tools (no direct filesystem writes).

Expected tool namespaces (based on existing conventions in this repo):
- Neo4j (lookup): `mcp__neo4j-aura__get_neo4j_schema`, `mcp__neo4j-aura__read_neo4j_cypher`
- HITL capture: `mcp__hitl__submit_knowledge`, `mcp__hitl__get_submission_status`, `mcp__hitl__list_submissions`
- HITL review: `mcp__hitl_review__list_submissions`, `mcp__hitl_review__get_submission`, `mcp__hitl_review__record_review`

Note: `.claude/mcp.json` is gitignored in this repo; wiring is expected to be local.

Note: `.claude/mcp.json` is gitignored in this repo; wiring is expected to be local.

### Logging hook compatibility
Prompts must require a test id in this exact format:

```
[TEST_ID: XX-XXXXXX]
```

So existing hooks can capture the run and append to `test_log.csv`.

## Execution steps
1. Create `.claude/agents/vmrs-lookup-hitl-runner.md`
   - Start from the same Neo4j schema + query guidelines as the VMRS lookup agent
     (see `interface prompts/lookup_agent/main_v4.txt`).
   - Include HITL capture behavior: when operator feedback is present, call `submit_knowledge`.
   - Verify submission exists via `get_submission_status`.

2. Create `.claude/agents/hitl-review-runner.md`
   - Pattern after the HITL review agent UX (see `interface prompts/hitl_review_agent/main_v3.txt`).
   - Lists pending submissions, fetches one, records a decision, and confirms it appears in approved/rejected.

3. (Optional) Keep `.claude/agents/hitl-capture-runner.md` as a low-level smoke test for the capture MCP tools.

4. Add/ensure `Closes #27` and `Closes #28` in the PR description.

## Acceptance criteria
- [ ] `vmrs-lookup-hitl-runner` exists under `.claude/agents/` and includes both:
  - Neo4j lookup tools
  - HITL capture tools
- [ ] `hitl-review-runner` exists under `.claude/agents/` and references the review MCP tools.
- [ ] Prompts require `[TEST_ID: ...]` in the invoking prompt.
- [ ] A developer can run an end-to-end manual test:
  - Integration runner answers a lookup question and (when feedback is present) creates a pending submission in `HitL_local/pending/`.
  - Review runner moves it to `HitL_local/reviewed/{approved|rejected}/`.

Optional:
- [ ] `hitl-capture-runner` remains available as a capture MCP smoke test.

## Manual test recipes

### VMRS lookup + HITL capture (integration) — canonical ambiguity case

Canonical case from the last test suite:
- `tests/test_questions/conversations/DP-3dd466.md`
- Original question: `What is the VMRS code for "DRIVERS SIDE SEAT"?`
- Why it matters: ambiguous phrasing can be interpreted as seat assembly vs seat belt; we want the lookup agent to either ask a clarifying question or allow the operator to correct and then capture that correction into HITL.

Prompt template (Claude Code subagent run):
```
[TEST_ID: VL-DP-3dd466]
Lookup: What is the VMRS code for "DRIVERS SIDE SEAT"?

Operator feedback: This is ambiguous — I actually mean DRIVER SIDE SEAT BELT (not the seat assembly). Please record this as HITL feedback.
Submitter: name=Test Submitter, role=technician
```

Expected:
- Lookup behavior: returns ranked candidates and/or asks a clarifying question (seat vs seat belt).
- HITL behavior: creates a pending submission via `submit_knowledge`.
- Verification: a new JSON exists under `HitL_local/pending/` (or `get_submission_status` returns found/pending if you check via tool).

### Review (APPROVE path)
Prompt:
```
[TEST_ID: HR-000001]
Review the newest pending HITL submission as approved (operator_name "Test Operator"; operator_role "reviewer"), then confirm it shows up in the approved list.
```

Expected:
- `record_review` returns `status=success`.
- Approved list contains the id.

### Review (REJECT path)
Prompt:
```
[TEST_ID: HR-000002]
Review the newest pending HITL submission as rejected (operator_name "Test Operator"; operator_role "reviewer"), include a short reason in review_notes, then confirm it shows up in the rejected list.
```

Expected:
- `record_review` returns `status=success`.
- Rejected list contains the id.

### (Optional) Capture MCP smoke test
Prompt:
```
[TEST_ID: HC-000001]
Create a minimal HITL submission for VMRS 047-000-000 describing a small correction, then verify it exists.
```

Expected:
- Tool returns `status=success` with an `id`.
- `get_submission_status` returns found/pending.
