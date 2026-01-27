# Plan: Issue #17 — HITL storage format (JSON vs SQLite/DB) + schema evolution

## 0. Executive Summary
We will choose a storage approach for HITL records that matches VMRS’s near-term needs (local + early deployments) while keeping an explicit path to multi-device/multi-tenant production. The decision should be driven by concrete query requirements, concurrency guarantees, and schema evolution discipline. Near-term, JSON is acceptable for local MVP if we enforce atomic writes + idempotency + strict validation; SQLite is the recommended “early prod” middle ground once we need reliable querying and stronger integrity.

**Ask (decisions needed to proceed):**
- Confirm the minimum query set we must support in beta/pilot/prod (listed below).
- Confirm schema evolution posture: record-level `schema_version` + read-time upcasting (recommended) vs write-time migrations.

## 1. Introduction / Purpose
- Purpose: decide storage + define schema evolution/migration strategy for HITL records.
- Audience: maintainers implementing HITL capture/review and operators consuming HITL history.
- Decision enabled: select storage approach for beta/pilot/prod and the evolution strategy.

## Links
- Issue #17: https://github.com/Dodhon/vmrs/issues/17
- Current local storage: `HitL_local/{pending,reviewed}/` JSON files
- Canonical schema/versioning: `src/hitl_schema.py` (`SCHEMA_VERSION`)

## Goal
Decide the long-term storage approach for HITL records and define a schema evolution strategy that supports:
- querying and reporting (status/date/operator/vmrs_code/etc.)
- concurrency safety + corruption resistance
- migrations/back-compat with explicit versioning
- rollback friendliness (ties to CI/CD Issue #16)

## Functional requirements
FR1. Storage must support the minimum query set (Q1–Q8) for beta/pilot/prod.
FR2. Writers (capture + review) must validate inputs against the canonical schema before persistence.
FR3. Records must include a `schema_version` field (record-level) for compatibility decisions.
FR4. Data must be exportable for debugging/auditing (human-readable or tool-exportable).

## Non-functional requirements
NFR1. Atomicity: writes must not produce partial/corrupt records, even on crash.
NFR2. Concurrency: review persistence must remain idempotent under concurrent attempts.
NFR3. Rollback friendliness: a rollback should not require irreversible data migrations in normal operation.
NFR4. Operational simplicity: local dev should remain easy; early prod should not require heavy ops.

## Minimum query requirements (beta/pilot/prod)
These queries are the decision driver. If we can’t satisfy them cleanly with JSON, we should move to SQLite.

- Q1. List pending submissions (most recent N).
- Q2. Get a submission by `submission_id`.
- Q3. List reviewed submissions by decision (approved/rejected) and date range.
- Q4. Filter reviewed submissions by operator (name/role or principal id) and date range.
- Q5. Filter by domain keys (e.g., `vmrs_code`, component/vendor identifiers) as available.
- Q6. Show “review throughput” metrics (counts per day/week, approval rate).
- Q7. Support audit questions: “who approved what, when?” including immutable decision record.
- Q8. Support schema evolution: load old records and interpret them under current code.

## Schema evolution strategy (recommended)
- Record-level `schema_version` on every persisted record.
- Prefer **read-time upcasting**: when reading an older version, transform it in-memory to the current shape.
- Use write-time migrations only when strictly necessary (e.g., performance or query/index changes), and gate them behind explicit tooling.

## Non-goals (for this issue)
- Implementing the full production storage system (may be a follow-on)
- Perfect analytics layer

## Current state (repo-grounded baseline)
- HITL records are JSON files under `HitL_local/`:
  - pending: `HitL_local/pending/*.json`
  - reviewed: `HitL_local/reviewed/{approved|rejected}/*.json`
- The review MCP server (`mcp/hitl_review/server.py`) already:
  - validates review inputs via `src/hitl_schema.validate_review_input`
  - moves pending → reviewed via an atomic staging move (pending → staging → reviewed)
  - writes reviewed JSON atomically and refuses overwrite
- Canonical schema + versioning lives in `src/hitl_schema.py` (`SCHEMA_VERSION=2`) and CI enforces the prompt excerpt is up to date.
- Current automated tests include `tests/test_hitl_schema.py` (validation + excerpt determinism).

## Options
### Option A — Keep JSON files (status quo)
Pros:
- simplest; human-readable; easy local dev
- file-based workflows are easy to inspect/debug
Cons:
- querying becomes painful (need indexing layer)
- concurrency and partial-write hazards (must be handled carefully)
- schema migrations are ad hoc without tooling

### Option B — SQLite (recommended middle ground for early prod)
Pros:
- single portable file; transactional writes; better concurrency than JSON files
- easy queries (SQL); straightforward indexing
- migrations possible (Alembic or simple versioned scripts)
Cons:
- introduces DB layer + migration discipline
- remote/multi-instance patterns require more care

### Option C — Postgres (or similar)
Pros:
- robust concurrency; multi-tenant; strong tooling
- easy to build dashboards/analytics
Cons:
- higher ops cost/complexity

### Option D — Object storage + index (S3 + DB)
Pros:
- scalable storage for large blobs
- separate index for queries
Cons:
- most complex; probably premature for MVP

## Evaluation criteria (what we should measure)
- Query needs (MVP vs prod): filter by decision/status/date/operator/vmrs_code/type/submitter
- Concurrency + corruption resistance
- Schema evolution strategy:
  - record-level `schema_version`
  - read-time upcasting vs write-time migrations
  - validation location (tool boundary vs storage boundary)
- Auditability and immutability (append-only? revision history?)
- Rollback friendliness (restore previous artifact + data)
- Operational complexity (local dev, beta, prod)

## Proposed recommendation (tentative)
- Short-term: keep JSON for local MVP, but enforce strict atomic writes + idempotency + bounded payloads.
- Medium-term: migrate to SQLite when:
  - you need queries beyond “latest N”, OR
  - you introduce multi-device usage, OR
  - you need stronger auditability.
- Long-term: Postgres for multi-tenant + team workflows.

## Work breakdown
E1) Inventory current HITL read/write paths
- Enumerate all writers/readers of HITL JSON (capture + review + any tooling)

E2) Confirm minimal query requirements
- Validate Q1–Q8 against real use cases and update as needed

E3) Choose storage for beta/pilot/prod
- Decide: JSON vs SQLite vs Postgres
- Define whether multi-tenant is expected (affects schema)

E4) Schema evolution plan
- Define how we version, validate, and upcast
- Define when (if ever) we do write-time migrations

E5) Migration plan (if moving off JSON)
- One-time conversion tool + verification (counts, sampling, hashes)
- Rollback strategy

## Acceptance criteria
- [ ] Choose a storage approach for beta/pilot/prod (and why)
- [ ] Define schema versioning + migration approach
- [ ] Document migration plan from current JSON if needed
- [ ] Identify minimal query needs and how they’ll be served
