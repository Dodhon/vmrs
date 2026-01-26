# Plan: Issue #15 — Deterministic, schema-validated HITL review decisions

## Links
- Issue #15: HITL review agent: make approval decision deterministic and schema-validated
- Review MCP server: `mcp/hitl_review/server.py`
- Schema/validation helpers: `src/hitl_schema.py`

## Goal
Ensure HITL review outcomes are **unambiguous**, **machine-checkable**, and **durably recorded** so downstream automation never depends on free-text interpretation.

## Non-goals
- Applying approved changes into Neo4j (review is a gate only)
- Storage backend migration (tracked separately)

## Research / best practices (with sources)
These sources converge on the same core idea: approvals should be explicit, schema-validated, and durably recorded.

### 1) Gate high-stakes actions at the tool boundary
- HITL is best implemented as: agent attempts a protected action → system pauses for human approval → approval/denial drives execution.
- Key operational detail: approval should not be inferred from prose; it should be explicit and structured.
Source: Letta HITL guide
- https://docs.letta.com/guides/agents/human-in-the-loop/

### 2) Validate decisions against a schema (including enums)
- MCP’s elicitation model uses a JSON schema for structured user input and explicitly supports enum schemas.
- It also distinguishes user actions as accept/decline/cancel (important to avoid “skip” being ambiguous).
Source: MCP spec (elicitation)
- https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation

### 3) Durable approvals; avoid duplicate approvals
- Durable workflow patterns emphasize storing approvals such that crashes/timeouts don’t require re-approval.
- Avoid re-processing the same approval and ensure idempotent review recording.
Source: Temporal tutorial (durable HITL)
- https://learn.temporal.io/tutorials/ai/building-durable-ai-applications/human-in-the-loop/

### 4) Provide reviewers necessary context and require actionable feedback
- Review checkpoints should include enough context and capture clear denial reasons (actionable guidance).
Source: Letta (clear denial reasons) + Cloudflare (state consistency, review history)
- https://docs.letta.com/guides/agents/human-in-the-loop/
- https://developers.cloudflare.com/agents/concepts/human-in-the-loop/

### 5) Typed approval payloads are common in production examples
- Typed schemas (e.g., Zod/JSON-schema) for approval payloads + validation on resume are common.
Source: Workflow DevKit example
- https://useworkflow.dev/docs/ai/human-in-the-loop

## Options (evaluate)
### Option A — Prompt-only discipline (weak)
- Tighten the review agent prompt to force deterministic text.
- Risk: LLM drift; still ambiguous unless enforced server-side.

### Option B — Tool-boundary enforcement (strong baseline)
- Persist decisions only via MCP tool call with an enum outcome.
- Server validates inputs; never writes ambiguous outcomes.

### Option C — Two-phase: recommendation vs decision (best UX + safety)
- Agent can provide a recommendation, but persisted decision is an explicit operator choice.
- Persisted record remains structured; recommendation is optional.

### Option D — JSON-object output with retry/reprompt (only if needed)
- If you ever want the model to emit JSON review objects directly, validate JSON (pydantic/jsonschema) and retry until valid.

## Proposed approach (recommended)
Implement **Option B** (tool-boundary enforcement) plus a small UX refinement from **Option C**:
- Persist only via `record_review(...)` with `outcome` enum.
- Require `review_notes` and reviewer identity fields.
- Ensure idempotency/no-overwrite and atomic move/write so you never double-review.

## Key decisions to make
1) Do we support “Skip” as a first-class persisted state?
   - Recommendation: treat skip as “cancel” (not persisted) OR persist as a distinct value (e.g., `skipped`) but never conflate with reject.
2) Canonical casing: `approved/rejected` vs `APPROVE/REJECT`.
3) Canonical storage location for review fields (ties to issue #38):
   - Recommend `review.{decision, reviewed_at_ms, notes, operator}` as canonical.

## Work breakdown
E1) Harden server-side validation
- Ensure outcome is restricted to enum.
- Ensure `review_notes` is required and non-empty.
- Ensure `operator_name` and `operator_role` are required and non-empty.

E2) Ensure deterministic persistence
- Review tool must never write ambiguous output.
- Atomic move/write; no overwrite.

E3) Update prompts / runner tests
- Review agent asks operator for Approve/Reject (and required reason).
- Add explicit test cases: approve path + reject path.

## Validation plan
V1) Unit-style validation
- Invalid outcomes rejected.
- Missing `review_notes` rejected.
- Missing operator identity rejected.

V2) End-to-end manual
- Create a pending submission.
- Record approve and verify file moved to `HitL_local/reviewed/approved/`.
- Record reject and verify file moved to `HitL_local/reviewed/rejected/`.
- Confirm reviewed records are machine-parseable and consistent.
