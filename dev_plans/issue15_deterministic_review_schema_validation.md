# Plan: Issue #15 — Deterministic, schema-validated HITL review decisions

## 0. Executive Summary
We will make HITL review outcomes deterministic by treating the MCP server tool call as the sole source of truth for persisted decisions (never inferred from prose). The server will validate a strict decision schema, record decisions durably and idempotently (no duplicates, crash-safe), and harden the filesystem write path against bad inputs (path traversal, unbounded payload sizes). This plan also establishes a production seam for authentication/authorization and multi-tenant scoping without forcing a storage migration yet.

**Ask (decisions needed to proceed):**
- Decide skip semantics: is “Skip” (a) a no-op that leaves a submission pending, or (b) a persisted state/event?
- Decide notes policy: are notes required for approve, or only for reject?
- Decide canonical field names/enums for review payloads (e.g., `notes` vs `review_notes`, enum casing).

## 1. Introduction / Purpose
- Purpose: define how we will guarantee **unambiguous**, **machine-checkable**, and **durably recorded** HITL review decisions.
- Audience: maintainers and implementers of `mcp/hitl_review/server.py` and the HITL schema/prompt surface.
- Decision enabled: accept the plan (incl. the three asks above) so implementation can proceed without re-litigating semantics.

## Links
- Issue #15: HITL review agent: make approval decision deterministic and schema-validated
- Review MCP server: `mcp/hitl_review/server.py`
- Schema/validation helpers: `src/hitl_schema.py`

## Executive summary (for manager feedback)
We need HITL review decisions to be **deterministic at the tool boundary** (never inferred from free text), **schema-validated**, and **durably recorded** so downstream automation (including knowledge graph releases in Issue #16) can trust them.

The repo is already close: the review MCP server validates inputs, refuses overwrite, and performs an atomic pending→staging→reviewed flow. The remaining work is to close ambiguity gaps (Skip semantics), harden against bad inputs (path safety + payload bounds), and add audit fields (`review_id`, `submission_hash`) so approvals are replay-safe and traceable.

Manager input requested (high-signal decisions):
- **Skip/cancel semantics:** confirm that Skip/Cancel results in *no persisted decision* and the submission remains pending (vs adding a third state).
- **Notes policy:** confirm whether notes are required for reject only (recommended) or for both approve+reject.
- **Tenant model assumption:** confirm single-tenant MVP vs designing for multi-tenant now (recommended to make `tenant_id` additive).
- **Identity/auth seam:** confirm the expectation for when “real” AuthN/AuthZ must exist (local stub now vs immediate).
- **Cross-issue alignment:** confirm how review artifacts should be stored/served as the canonical “approved HITL” dataset (ties to Issue #17 storage decisions and Issue #16 graph releases).

## Goal
Ensure HITL review outcomes are **unambiguous**, **machine-checkable**, and **durably recorded** so downstream automation never depends on free-text interpretation.

## Functional requirements
FR1. The only persisted decision record is created by a validated server-side tool call (not by parsing model prose).
FR2. The server only persists allowed outcomes (enum); invalid outcomes never produce a reviewed artifact.
FR3. A given submission can be reviewed at most once; repeated attempts return the existing recorded outcome (idempotent).
FR4. Review records include sufficient metadata to link the decision to the reviewed submission (submission_id + reviewed_at_ms at minimum).
FR5. “Skip” is handled consistently across clients and server (see Ask above); there is no ambiguous partial persistence.

## Non-functional requirements
NFR1. Persistence is crash-safe and atomic: no partial reviewed records, and no silent overwrite.
NFR2. Concurrency-safe: two concurrent review attempts cannot create two different reviewed records.
NFR3. Path-safe: submission identifiers cannot cause path traversal or writes outside expected directories.
NFR4. Bounded inputs: server enforces maximum sizes/lengths to mitigate DOS/storage bloat.
NFR5. Deterministic output: reviewed artifacts must be machine-parseable and stable in structure.

## Architecture diagram (runtime + storage)
### High-level (system context)
```
Operator/Reviewer (human)
        |
        v
Review Agent UI / Client
        |
        v
MCP Tool: mcp/hitl_review/server.py  ---->  HitL_local/* (pending/reviewed)
        |
        v
Downstream automation reads reviewed artifacts (never model prose)
```

### Low-level (containers + data stores)
```
+------------------------+        +------------------------------+
| Review client/agent UI |  MCP   | hitl_review MCP server       |
| (Approve/Reject/Skip)  | -----> | - validate_review_input       |
+------------------------+        | - lock per submission_id      |
                                  | - atomic move/write           |
                                  +---------------+--------------+
                                                  |
                                                  v
                                     +-----------------------------+
                                     | Local filesystem storage     |
                                     | HitL_local/pending/*.json    |
                                     | HitL_local/reviewed/...      |
                                     +-----------------------------+
```

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

## Repo status vs this plan (as of today)
This section is a quick reality check so implementation work is scoped correctly.

### Already implemented in repo (baseline is stronger than a blank slate)
- **Tool-boundary enforcement exists**: `mcp/hitl_review/server.py` exposes `record_review(...)` and persists review outcomes only via this tool.
- **Server-side validation exists**: `src/hitl_schema.validate_review_input(...)` enforces:
  - `outcome ∈ {approved, rejected}`
  - `review_notes` required
  - `operator_name` and `operator_role` required
- **Deterministic file movement + overwrite refusal**:
  - `record_review` refuses to overwrite if a reviewed destination exists.
  - It does an atomic move out of pending (`pending → staging`) before writing the reviewed file, reducing double-review risk.
- **Canonical schema source exists**: `src/hitl_schema.py` owns `SCHEMA_VERSION` and prompt-safe schema excerpt.
- **Reviewed JSON shape is mostly aligned**:
  - writes `review.{decision, reviewed_at_ms, notes, operator}`
  - mirrors legacy top-level fields for back-compat
  - writes to `HitL_local/reviewed/{approved|rejected}/<id>.json` and sets `status = "reviewed"`

### Not yet implemented / mismatches (work required)
- **Skip/cancel semantics are not enforced end-to-end**:
  - Review agent prompt offers Approve/Reject/Skip, but the server tool only accepts approved/rejected.
  - Decide whether “Skip” is a no-op (no tool call; remains pending) and ensure all clients behave identically.
- **Bad-actor hardening is missing** (critical for plugin-anywhere future):
  - Path safety: `submission_id` is used to form paths; add strict ID validation to prevent traversal.
  - Bounded payload sizes: add max lengths to prevent DOS / storage bloat.
- **Principal/Auth seam is missing**:
  - Current operator identity is user-supplied text; not trustworthy for prod.
  - Introduce a server-derived `principal` model (local stub now, real auth in prod).
- **Policy alignment needed**:
  - Current code requires notes for both approve and reject; plan proposes reject-required / approve-optional (choose one).
- **Auditability fields not yet added**:
  - `review_id` (server generated) and `submission_hash` (hash of pending payload at review time).
- **Tenant scoping not present**:
  - If multi-tenant is likely, design now so `tenant_id` can be additive (optional now, required later).

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
  - lock (per submission_id) using a lockfile created with exclusive create (e.g., `O_EXCL`) and a short timeout
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
