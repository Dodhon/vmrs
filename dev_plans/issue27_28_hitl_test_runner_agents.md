# Plan: HITL Test Runner Sub-Agents (Issues #27, #28)

## Links
- Issue #27: Add test runner agent for HITL capture MCP server (`mcp/hitl_get_feedback`)
- Issue #28: Add test runner agent for HITL review MCP server (`mcp/hitl_review`)
- Existing runner: `.claude/agents/vmrs-test-runner.md`
- Capture server: `mcp/hitl_get_feedback/server.py`
- Review server: `mcp/hitl_review/server.py`

## Goal
Add **two minimal test runner sub-agents** (similar to `vmrs-test-runner`) so we can exercise the HITL MCP servers in isolation.

End state: **3 total test runner agents**
- `vmrs-test-runner`
- `hitl-capture-runner`
- `hitl-review-runner`

## Non-goals
- Changing HITL schema or storage layout (tracked separately)
- Changing the capture/review MCP servers beyond what is required to run tests

## Design
### Agent locations
Add new sub-agent configs under:
- `.claude/agents/hitl-capture-runner.md`
- `.claude/agents/hitl-review-runner.md`

### Tool wiring
The agents should call MCP tools (no direct filesystem writes).

Expected tool namespaces (based on local Claude MCP config):
- Capture: `mcp__hitl__submit_knowledge`, `mcp__hitl__get_submission_status`, `mcp__hitl__list_submissions`
- Review: `mcp__hitl_review__list_submissions`, `mcp__hitl_review__get_submission`, `mcp__hitl_review__record_review`

Note: `.claude/mcp.json` is gitignored in this repo; wiring is expected to be local.

### Logging hook compatibility
Prompts must require a test id in this exact format:

```
[TEST_ID: XX-XXXXXX]
```

So existing hooks can capture the run and append to `test_log.csv`.

## Execution steps
1. Create `.claude/agents/hitl-capture-runner.md`
   - Similar style to `vmrs-test-runner`
   - Includes minimal-valid `submit_knowledge` workflow
   - Verifies submission exists via `get_submission_status` (and optionally `list_submissions`)

2. Create `.claude/agents/hitl-review-runner.md`
   - Similar style to `vmrs-test-runner`
   - Lists pending submissions
   - Gets one submission
   - Records an approved/rejected decision
   - Confirms it appears in the destination list

3. Add/ensure `Closes #27` and `Closes #28` in the PR description.

## Acceptance criteria
- [ ] `hitl-capture-runner` exists under `.claude/agents/` and references only the capture MCP tools.
- [ ] `hitl-review-runner` exists under `.claude/agents/` and references only the review MCP tools.
- [ ] Both prompts require `[TEST_ID: ...]` in the invoking prompt.
- [ ] A developer can run an end-to-end manual test:
  - Capture runner creates a pending submission in `HitL_local/pending/`.
  - Review runner moves it to `HitL_local/reviewed/{approved|rejected}/`.

## Manual test recipes
### Capture
Prompt:
```
[TEST_ID: HC-000001]
Create a minimal HITL submission for VMRS 047-000-000 describing a small correction, then verify it exists.
```

Expected:
- Tool returns `status=success` with an `id`.
- `get_submission_status` returns found/pending.

### Review
Prompt:
```
[TEST_ID: HR-000001]
Review the newest pending HITL submission as approved (operator_name "Test Operator"; operator_role "reviewer"), then confirm it shows up in the approved list.
```

Expected:
- `record_review` returns `status=success`.
- Approved list contains the id.
