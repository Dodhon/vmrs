# HITL Step 2 Plan: Operator Review (MVP)

This plan defines **Step 2** of the HITL MVP: the **initial version of an operator reviewing feedback** captured in Step 1.

## References
- `HitL_local/hitl_design.md` (design rationale + recommended JSON fields)
- `dev_plans/hitl_plan.md` (MVP steps + local storage layout)

## Goal (Step 2)
Provide a minimal **agent-led** review workflow where a **non-technical operator** can:
- Review submissions stored in `HitL_local/pending/` (the agent fetches and summarizes them)
- Provide a review outcome (**approved** or **rejected**) and a short **why** (justification) in plain language
- Have the agent persist the review decision by moving the submission out of `pending/`

## Prompt visibility constraint (important)
The review agent may only be able to see text in `interface prompts/hitl_review_agent/`.
- Keep the review prompt **self-contained** (do not reference other prompt folders for required instructions).

## Flow (ASCII)
```
Step 1 (capture)                          Step 2 (operator review)
-----------------                         -----------------------
Agent / MCP tool
  |
  v
HitL_local/pending/<id>.json  ----->  Review Agent (talks to operator)
                                      |  (uses MCP tools; operator is non-technical)
                                      |
                                      v
                                 Operator says: approved|rejected (+notes)
                                      |
                                      v
                         agent calls MCP tool to record review + move file
                                      |
                                      v
                      HitL_local/reviewed/approved/<id>.json
                      HitL_local/reviewed/rejected/<id>.json

On review:
- status: pending -> approved|rejected
- add: reviewed_at_ms, reviewed_by, review_notes, decision
```

## Sample workflow (what it looks like)
High level: the agent drives everything; the operator only answers in plain language.

```
Operator: "Let's review the next feedback item."

Agent: (calls MCP) list_submissions(limit=5)
Agent: "I found 5 pending items. Reviewing the oldest next."
Agent: (calls MCP) get_submission(submission_id="HITL-...")  # or picks from list
Agent: "Summary:
- Type: correction
- VMRS code: 047-000-000
- Description: <short description>
- Context: <if present>

Do you APPROVE this feedback (it looks correct and should be incorporated later),
or REJECT it (not correct / not actionable)?"

Operator: "Approve. Because the user provided a handbook screenshot as evidence."

Agent: (calls MCP) record_review(
  submission_id="HITL-...",
  outcome="approved",
  reviewed_by="<operator name or initials>",
  review_notes="user provided a handbook screenshot"
)
Agent: "Saved. This item is now marked approved and moved out of pending."
```

## Non-goals (explicitly out of scope)
- Applying approved changes into Neo4j / the published KG
- Multi-stage workflows (`in_review`, re-review, appeals), provenance event graphs, ranking
- Capturing full Claude chat transcripts (keep `HitL_local/conversations/` unused for now)

## Storage layout (file-first)
Current (Step 1):
- `HitL_local/pending/<id>.json`

Step 2 adds reviewed storage. 
- `HitL_local/reviewed/approved/<id>.json`
- `HitL_local/reviewed/rejected/<id>.json`



## Invariants (minimal integrity rules)
- **Filename must match JSON**: `<id>.json` must contain `"id": "<id>"` (otherwise treat as invalid and skip).
- **Only review pending**: input files must have `"status": "pending"` (otherwise treat as invalid and skip).

## Submission JSON updates on review (minimal + compatible)
When a submission is reviewed, keep existing fields and append review metadata:

- Update:
  - `status`: `pending` → `approved` or `rejected`
- Add:
  - `reviewed_at_ms`: integer epoch millis (UTC)
  - `review_notes`: string (**required**; why approved/rejected)
  - `reviewed_by`: string (operator name or id)
  - `decision`: `approved` or `rejected`

This keeps the JSON shape compatible with a future Neo4j `(:HitlSubmission {...})` node.

## Review tooling: MCP server tools (agent-facing)
Step 2 review is implemented via MCP tools in a **separate MCP server under `mcp/`** (not `mcp/hitl/server.py`).

Important:
- `mcp/hitl/server.py` remains the **capture-only** server (Step 1).
- Step 2 introduces a **review** MCP server (suggested path: `mcp/hitl_review/server.py`).
- Rationale: keep **one MCP server per agent** (capture vs review) to reduce cross-scope coupling.
- The operator never touches JSON or the filesystem.

### Tools (minimal)
- `list_submissions(limit=10, location="pending")`
  - Used by the agent to find pending work.
- `get_submission(submission_id)`
  - Returns the full JSON for the submission (so the agent can summarize it for the operator).
- `record_review(submission_id, outcome, reviewed_by, review_notes)`
  - Validates the submission is pending, updates the JSON, and moves it to reviewed storage.

### Robustness requirements (still minimal)
- **Atomic move/write**: avoid partial files (write temp + rename; then move).
- **No overwrite**: if reviewed destination already exists, fail fast.
- **Invalid JSON handling**: surface the error and skip (do not auto-fix in Step 2).

## Implementation checklist (Step 2)
- Create a review MCP server under `mcp/` (suggested: `mcp/hitl_review/server.py`):
  - Ensure reviewed directories exist:
    - `HitL_local/reviewed/approved/`
    - `HitL_local/reviewed/rejected/`
  - Implement tools:
    - `get_submission`
    - `record_review` (approved|rejected; `review_notes` required “why”)
- Create a dedicated **HITL review agent prompt** and define the agent context:
  - Prompt file: `interface prompts/hitl_review_agent/main_v1.txt`
  - Context should include: how to present a submission to a non-technical operator, the approved/rejected rubric, and what is explicitly out of scope (no Neo4j writes).

## Acceptance criteria (definition of “done”)
- A submission in `HitL_local/pending/` can be reviewed end-to-end:
  - Agent can list pending submissions and fetch a full submission via MCP tools
  - Operator can choose approved/rejected in plain language
  - After recording, the file is **no longer** in `pending/` and is present in the reviewed destination
  - JSON includes `status`, `decision`, `reviewed_at_ms`, `reviewed_by`, `review_notes`
- Works for both:
  - Structured intent submissions (`target_type`, `target_key`, `proposed_action`, `proposed_payload`)
  - “Free text” submissions that only contain `description/context`

