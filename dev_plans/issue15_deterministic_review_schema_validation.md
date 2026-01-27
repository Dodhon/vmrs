# Plan: Issue #15 — Deterministic, schema-validated HITL review decisions

## Links
- Issue #15: HITL review agent: make approval decision deterministic and schema-validated
- Review MCP server: `mcp/hitl_review/server.py`
- Schema/validation helpers: `src/hitl_schema.py`

## Goal
Ensure HITL review outcomes are **unambiguous**, **machine-checkable**, and **durably recorded** so downstream automation never depends on free-text interpretation.

## Threat model / context
This system will be exposed as an agent “plugin” across sites/devices (e.g., Copilot-style). Treat **callers as untrusted by default**.

We want an identical, deterministic experience for:
- legitimate operators
- sloppy users
- bad actors

So the server must enforce determinism + safety regardless of who is interacting.

## Non-goals
- Applying approved changes into Neo4j (review is a gate only)
- Storage backend migration (tracked separately)

## Local MVP vs Production (what differs)
### Local MVP (single-machine)
Minimum to ship safely while keeping the architecture compatible with prod:
- Tool-boundary decision recording + strict schema validation
- Write-once, idempotent persistence (no overwrite)
- Path safety (no traversal) + bounded payload sizes (basic DOS resistance)
- “Authenticated principal” interface exists, even if the principal is hardcoded locally (do not treat user-supplied `operator` fields as security)
- Add `submission_hash` + server-generated `review_id` now (cheap, future-proof)

### Production (plugin accessible anywhere)
Additional requirements because the surface is untrusted:
- Real AuthN/AuthZ for review actions (who can approve/reject, and for what scope)
- Replay resistance / request integrity (prevent replaying an approval)
- Rate limiting + quotas + retention policy
- Durable storage with atomic conditional writes (DB/object store) + append-only audit trail

## Tenant model options (include both; decide later)
We may be either single-tenant or multi-tenant.

### Option 1 — Single-tenant (simpler)
- One global backlog + one reviewer pool
- All records share one namespace
- Still requires AuthN/AuthZ (bad actors exist), but no tenant scoping

### Option 2 — Multi-tenant (recommended for “plugin anywhere”)
- Every submission/review is scoped by `tenant_id` (org/workspace)
- Authorization is evaluated within a tenant
- Storage paths/keys include tenant scoping to prevent cross-tenant reads/writes

**Plan implication:** design schemas and storage keys so adding `tenant_id` later is additive (e.g., optional now, required in prod).

## Research / best practices (with sources)
These sources converge on the same core idea: approvals should be explicit, schema-validated, and durably recorded.

### 1) Gate high-stakes actions at the tool boundary
- HITL is best implemented as: agent attempts a protected action → system pauses for human approval → approval/denial drives execution.
- Key operational detail: approval should not be inferred from prose; it should be explicit and structured.
Source: Letta HITL guide
- https://docs.letta.com/guides/agents/human-in-the-loop/

### 2) Validate decisions against a schema (including enums) + distinguish cancel/decline
- MCP’s elicitation model uses a JSON schema for structured user input and explicitly supports enum schemas.
- It distinguishes user actions as accept/decline/cancel, which prevents “skip” ambiguity.
Source: MCP spec (elicitation)
- https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation

### 3) Durable approvals; avoid duplicate approvals
- Durable workflow patterns emphasize storing approvals so crashes/timeouts don’t require re-approval.
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
Implement **Option B** (tool-boundary enforcement) plus a small UX refinement from **Option C**.

### Core guarantees (determinism)
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
- Require actionable notes on rejection.

### Security guarantees (bad-actor resistance)
These should hold even if a caller is malicious:
- **AuthN/AuthZ gate for review writes** (prod): only authorized principals can persist decisions.
- **Write-once reviewed artifacts**: never overwrite silently.
- **Path safety**: validate identifiers used in paths (no traversal).
- **Bounded payload sizes**: prevent disk/CPU blowups.
- **Replay-safe** (prod): approvals cannot be replayed to create inconsistent state.

### Notes requirement (reduce friction)
- `rejected` → `notes` required (min length >= 1)
- `approved` → `notes` optional

## Key design decisions to make (tight)
1) **Skip semantics (avoid ambiguity)**
- Treat “skip/cancel” as not persisted; keep submission pending.
- Treat explicit refusal separately from reject (don’t conflate).
(Conceptually mirrors MCP accept/decline/cancel separation.)

2) **Canonical casing + field names**
- Prefer lowercase enums: `approved | rejected`.
- Canonical field: `notes` (avoid mixing `review_notes` vs `notes`).

3) **Canonical review record shape** (ties to issue #38)
- Canonical shape:
  ```json
  {
    "schema_version": 1,
    "tenant_id": "optional-now-required-later",
    "submission_id": "...",
    "submission_hash": "...",
    "review": {
      "review_id": "...",
      "decision": "approved",
      "reviewed_at_ms": 1730000000000,
      "principal": {"id": "…", "source": "…"},
      "operator_display": {"name": "…", "role": "…"},
      "notes": "…"
    }
  }
  ```

4) **Metadata to prevent mismatched/duplicate approvals**
- Include:
  - `submission_hash` (hash of pending payload at review time)
  - `review_id` (server-generated UUID)
  - `schema_version`
- Optional prod:
  - `review_request_id` / tool_call_id (nonce) for replay resistance

## Work breakdown
E0) Threat-model hardening (MVP now; prod-ready seams)
- Define principal model (even if hardcoded locally) and ensure it is server-derived.
- Add payload bounds (max lengths / max total size).
- Validate identifiers used for filesystem paths.

E1) Harden server-side validation
- Ensure decision is restricted to enum.
- Ensure required fields are present.
- Enforce notes requirement by outcome:
  - rejected → notes required
  - approved → notes optional
- Decide/implement explicit “skip/cancel” semantics (no persisted decision).

E2) Deterministic persistence (crash-safe + no double-review)
- Implement an idempotent pattern:
  - lock (per submission_id)
  - check already-reviewed → return existing record
  - stage write + atomic rename
  - **no overwrite**

E3) Metadata + auditability
- Add `submission_hash` + server-generated `review_id`.
- Optional prod: add `review_request_id` and record an append-only audit event per attempt.

E4) Prompt/test updates
- Review agent asks for Approve/Reject/Skip, with “Skip” mapping to no persisted decision.
- Tests cover approve + reject + skip/cancel.

## Validation plan
V1) Validation (unit)
- decision not in enum → reject.
- missing required fields → reject.
- rejected with empty notes → reject.
- approved with empty notes → allowed.
- oversize payloads → reject.

V2) Persistence/idempotency (integration)
- Approve then re-submit same review attempt → returns existing record; no duplicates.
- Concurrency: two reviewers attempt same id → one wins; other sees already-reviewed.

V3) End-to-end manual
- Create a pending submission.
- Record approve and verify reviewed artifact created.
- Record reject and verify reviewed artifact created.
- Skip/cancel leaves submission pending.
- Confirm reviewed records are machine-parseable and consistent.
