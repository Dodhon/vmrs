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
- **Append-only history:** we do not rewrite history; when we need to add or correct information, we append a new event/record that supersedes prior records.
- **Write-once reviewed artifacts:** no silent overwrite; correction flows must be explicit.
- **Versioned records:** every HITL record has a `schema_version`.
- **Provenance completeness:** every submission includes who touched it, where it is in the pipeline, and the relevant information for every step up to the current step.
- **Production seam for identity/auth:** operator display fields are not security; in prod, principal identity should be derived from the environment (e.g., employee id from auth/logs) and only simulated via required fields in MCP/tooling (name + role for MVP).

---

## Decisions to lock (recommendations)

### D1) Decision contract (Issue #15)
**Persisted outcomes:** `approved | rejected | needs_clarification` (lowercase enums).

**Skip semantics:** “Skip” means **needs_clarification** (persisted), not “reject.”
- Rationale: in this product, ambiguity is common and must be tracked; “skip” is a defer/follow-up state.
- `needs_clarification` MUST include a reviewer-authored `question` (what is ambiguous / what input is needed).
- `needs_clarification` is **non-terminal**; it does not admit data into the canonical approved dataset.

**Notes policy:** notes are **required for all outcomes**.
- `approved` → notes required (justification/provenance for KG admission)
- `rejected` → notes required (actionable reason)
- `needs_clarification` → notes required + question required

**Idempotency:**
- A submission can be reviewed at most once.
- Repeated tool calls return the existing recorded decision (no duplicates).

**Correction policy:**
- Do not overwrite reviewed artifacts.
- Corrections are represented as a **superseding event** that points at (and logically supersedes) the prior decision.
- Prior decisions remain queryable for audit/context.

### D2) Storage format + schema evolution (Issues #17 + #47)
**Near-term (intern MVP, single-machine):** JSON files are acceptable if we enforce:
- atomic writes (temp → rename)
- strict schema validation at tool boundary
- bounded payload sizes
- path-safe identifiers
- idempotency + concurrency safety

**Near-term (intern MVP, but enterprise-aligned choice): SQLite now**
Because this is a knowledge-graph/MDM project and ambiguity follow-ups are expected (needs_clarification), a stateful store becomes valuable earlier. For the intern MVP, SQLite is the recommended default if any of the following are true:
- the workflow is more than one process/UI
- you need queue views (pending vs needs_clarification) and throughput metrics
- you want an append-only audit trail without file-move edge cases

SQLite guidance:
- model decisions/clarifications as an append-only event log + a current-state projection.
- assume one writer / short transactions; enable WAL mode if applicable.

**Early production (post-intern / scale-out): Postgres**
If/when you need multiple service instances writing concurrently or stronger HA/ops guarantees, migrate the same schema to Postgres. Keep an additive seam for `tenant_id` even if single-tenant initially.

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

3) Current-state projection:
   - Use a **state table** in SQLite updated transactionally from appended events (vs computing state on the fly).

4) Queue claim/lease semantics (MVP):
   - MVP uses idempotency only (no claim/lease) and assumes low reviewer concurrency; revisit with manager if duplicate-work becomes a problem.

5) Escalation policy:
   - Proposed: if an item sits in `needs_clarification` for 30 days, escalate to the fleet management team manager (and/or ping the team).
   - Confirm exact escalation target + whether the escalation is a notification only or changes workflow state.

6) MDM identity strategy:
   - VMRS codes are canonical by value and are the key property for matching parts.
   - Vendors/vendor parts are MDM entities (canonical ids + aliases + merge/supersede).
   - Confirm the “other/none-of-the-above” flow: capture proposed values now, queue entity creation/merge for later review.

7) KG update policy:
   - KG should not be updated until a HITL submission reaches a terminal decision (`approved` or `rejected`).
   - Confirm whether `rejected` updates the KG (e.g., adds negative evidence / suppression edges) or is stored only as audit history.

8) Export format for the approved dataset:
   - Prefer a zipped bundle with `manifest.json` + per-record JSON + hashes (CI/CD-friendly, reproducible, rollbackable).
   - Optionally include JSONL for streaming ingestion later.

---

## Next steps
1) Merge this plan PR.
2) Add a short comment to issues #15/#16/#17/#47 linking to this plan PR as the architecture contract.
3) Proceed with implementation PRs in small slices, using these locked decisions as the guardrails.
