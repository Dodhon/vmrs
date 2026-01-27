# Plan: Issue #17 — HITL storage format (JSON vs SQLite/DB) + schema evolution

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

## Non-goals (for this issue)
- Implementing the full production storage system (may be a follow-on)
- Perfect analytics layer

## Current state (baseline)
- HITL records are JSON files in the repo working directory under `HitL_local/`.
- Review flow moves pending → reviewed/{approved|rejected}.
- Schema is versioned (`schema_version`) and centralized in `src/hitl_schema.py`.

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

E2) Define minimal query requirements (operator + analytics)
- List queries we must support in beta/pilot/prod

E3) Choose storage for beta/pilot/prod
- Decide: JSON vs SQLite vs Postgres
- Define whether multi-tenant is expected (affects schema)

E4) Schema evolution plan
- Define how we version, validate, and migrate
- Decide on read-time upcasting vs write-time migrations

E5) Migration plan (if moving off JSON)
- One-time conversion tool + verification
- Rollback strategy

## Acceptance criteria
- [ ] Choose a storage approach for beta/pilot/prod (and why)
- [ ] Define schema versioning + migration approach
- [ ] Document migration plan from current JSON if needed
- [ ] Identify minimal query needs and how they’ll be served
