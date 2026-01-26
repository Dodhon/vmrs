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

### Guarantees this should provide
1) **Decision is captured at the boundary, not inferred from prose**
- Persisted truth comes only from the tool call (not the agent’s narrative).

2) **Decision payload is machine-checkable (enums + required fields)**
- Outcome is an enum.
- Required fields are validated server-side.

3) **Approval is durable and idempotent**
- One submission should produce at most one persisted decision record.
- Retries and concurrent attempts should return the already-recorded decision, not create duplicates.

4) **Reviewer context + actionable rejection reasons are captured**
- Capture enough context for review.
- Require (at least) actionable notes on rejection.

### Notes requirement (reduce friction)
- `rejected` → `review_notes` required (min length >= 1)
- `approved` → `review_notes` optional (or default)

## Key design decisions to make (tight)
1) **Skip semantics (avoid ambiguity)**
- Treat “skip/cancel” as not persisted; keep submission pending.
- Treat explicit refusal separately from reject (don’t conflate).
(Conceptually mirrors MCP accept/decline/cancel separation.)

2) **Canonical casing**
- Prefer lowercase enums: `approved | rejected` to reduce drift.

3) **Canonical review field placement** (ties to issue #38)
- Canonical shape:
  ```json
  {
    "schema_version": 1,
    "review": {
      "decision": "approved",
      "reviewed_at_ms": 1730000000000,
      "operator": {"name": "…", "role": "…"},
      "notes": "…"
    }
  }
  ```

4) **Metadata to prevent mismatched/duplicate approvals**
- Consider adding:
  - `submission_hash` (hash of the pending payload at review time)
  - `review_request_id` / server-generated review UUID
  - `schema_version`

## Work breakdown
E1) Harden server-side validation
- Ensure outcome is restricted to enum.
- Ensure required operator identity fields are non-empty.
- Enforce notes requirement by outcome:
  - rejected → notes required
  - approved → notes optional
- Decide/implement explicit “skip” semantics (no persisted decision).

E2) Deterministic persistence (crash-safe + no double-review)
- Implement an idempotent pattern:
  - lock (per submission_id)
  - check already-reviewed → return existing record
  - stage write + atomic rename
  - no overwrite
- Consider upgrading reviewed artifacts to per-submission directories to co-locate payload + review metadata.

E3) Metadata
- Add `submission_hash` and a server-generated review id, if we want stronger auditability.

E4) Prompt/test updates
- Review agent asks operator for Approve/Reject/Skip, with “Skip” mapping to no persisted decision.
- Tests cover approve + reject + skip/cancel.

## Validation plan
V1) Validation (unit)
- outcome not in enum → reject.
- missing operator fields → reject.
- rejected with empty notes → reject.
- approved with empty notes → allowed (if we adopt the low-friction rule).

V2) Persistence/idempotency (integration)
- Approve then re-submit same review attempt → returns existing record; no duplicates.
- Concurrency: two reviewers attempt same id → one wins; other sees already-reviewed.

V3) End-to-end manual
- Create a pending submission.
- Record approve and verify file moved to `HitL_local/reviewed/approved/`.
- Record reject and verify file moved to `HitL_local/reviewed/rejected/`.
- Skip/cancel leaves submission pending.
- Confirm reviewed records are machine-parseable and consistent.
