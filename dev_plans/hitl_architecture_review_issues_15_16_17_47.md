# HITL Architecture Review (Bundle): Issues #15, #16, #17, #47

## Objective / decision
**Objective:** Produce one coherent HITL architecture that makes approvals deterministic, storage reliable, and deployments/release pipelines trustworthy.

**Decision needed (from Thupten):** Approve this architecture bundle as the shared “contract” for HITL going forward, so implementation PRs can proceed issue-by-issue without re-litigating fundamentals.

## Scope
This document bundles and aligns the following GitHub issues:
- **#15** Deterministic, schema-validated HITL review decisions
- **#16** CI/CD pipeline for deploys + rollbacks + Knowledge Graph releases (beta/pilot/prod)
- **#17** HITL storage format (JSON vs SQLite/DB) + schema evolution
- **#47** Evaluate stateful storage for HITL status (pending queue)

## Why bundle these
These four issues are architectural, not “one feature each.” They define:
- what an approval *is* (contract + determinism)
- where the HITL truth lives (storage, schema evolution)
- how “approved HITL” becomes a release artifact for environments (CI/CD and graph releases)

Treating them as a single architecture review avoids inconsistent local fixes that later block releases.

---

## Architecture (high level)

### Canonical flow
1) **Capture** creates a pending HITL submission (structured JSON, schema-versioned)
2) **Review** persists an explicit decision via an MCP tool call (tool-boundary truth)
3) **Approved HITL dataset** becomes the only dataset eligible to feed beta/pilot/prod builds
4) **Release pipeline** builds and deploys versioned artifacts (including KG releases), with rollback

### Key invariants
- **Tool-boundary truth:** approvals/rejections are persisted only by validated server-side tool calls (never inferred from prose).
- **Deterministic decisions:** decisions are enum-based, machine-parseable, and idempotent.
- **Write-once reviewed artifacts:** no silent overwrite; correction flows must be explicit.
- **Versioned records:** every HITL record has a `schema_version`.
- **Production seam for auth:** operator display fields are not security; server-derived principal is the authority.

---

## Decisions to lock (recommendations)

### D1) Decision contract (Issue #15)
**Persisted outcomes:** `approved | rejected` (lowercase enums).

**Skip semantics:** `skip` is a **no-op** (no persisted decision; submission remains pending).
- Rationale: keeps the state machine minimal and makes “reviewed” a strong signal.
- Future: if we need “defer/needs-info,” add an explicit third state/event later.

**Notes policy:**
- `rejected` → notes **required** (actionable reason)
- `approved` → notes optional

**Idempotency:**
- A submission can be reviewed at most once.
- Repeated tool calls return the existing recorded decision (no duplicates).

**Correction policy:**
- Do not overwrite reviewed artifacts.
- Corrections require an explicit “reopen/resubmit” workflow (new submission id) or a superseding event record.

### D2) Storage format + schema evolution (Issues #17 + #47)
**Near-term (local MVP):** JSON files are acceptable if we enforce:
- atomic writes (temp → rename)
- strict schema validation at tool boundary
- bounded payload sizes
- path-safe identifiers
- idempotency + concurrency safety

**Early production (recommended pivot):** SQLite for HITL (single portable DB file) when any of these become true:
- need reliable queries beyond “latest N”
- multi-device use
- stronger integrity/audit requirements

**Schema evolution posture:**
- record-level `schema_version`
- prefer **read-time upcasting** (in-memory transform to current shape)
- avoid write-time migrations unless necessary

**Pending queue state (Issue #47):**
- For local MVP, file-based pending is fine (with locking and atomic moves).
- The “stateful DB for pending queue” becomes compelling exactly when:
  - multiple writers across devices/users, OR
  - we need robust queue operations (claim/lease/visibility timeouts), OR
  - we need high-confidence audit/history queries.

### D3) “Approved HITL” as a release input (Issue #16)
**Rule:** Only **approved** HITL participates in beta/pilot/prod builds.

**Artifact model:** Approved HITL is treated as a **versioned dataset** (exportable + checksummed) that CI/CD can consume deterministically.

**Release + rollback expectation:**
- Deployments must be attributable (who/what/where) and reversible.
- For Neo4j Aura in prod: prefer blue/green cutover; rollback is a fast URI/secret flip.

---

## Implications / how this changes our workflow

### What the issue board means vs dev_plans
- GitHub issues track **what** needs to be done.
- `dev_plans/` (this doc + per-issue plans) define **how** it will be done.

### What becomes “done” for this architecture bundle
This bundle is “done” when:
- the above decisions are ratified, and
- each of #15/#17/#47/#16 references this architecture as the shared contract.

Implementation can then proceed as separate PRs:
- PRs for #15 determinism + safety hardening
- PRs for #17 storage/evolution refactors
- PRs for #47 queue/stateful storage changes (if/when triggered)
- PRs for #16 CI/CD + release pipelines

---

## Open questions (explicit)
These should be answered in the issue threads or as follow-up decisions, but they do not block adopting the core contract:
1) For #16: confirm v1 deployment target + what beta/pilot/prod concretely mean.
2) For #17/#47: confirm minimum query set required in beta/pilot/prod (Q1–Q8 style list).
3) For #15: confirm whether we ever need “defer/needs-info” (separate from skip) as a persisted state.

---

## Next steps
1) Merge this plan PR.
2) Add a short comment to issues #15/#16/#17/#47 linking to this plan PR as the architecture contract.
3) Proceed with implementation PRs in small slices, using these locked decisions as the guardrails.
