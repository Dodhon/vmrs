# HITL Architecture Review (Bundle): Issues #15, #16, #17, #47

## Table of contents
- [Objective / decision](#objective--decision)
- [Manager response (copy/paste)](#manager-response-copypaste)
- [Decision summary (first-screen)](#decision-summary-first-screen)
- [Scope](#scope)
- [Architecture (high level)](#architecture-high-level)
- [Decisions to lock (contract)](#decisions-to-lock-contract)
- [Open questions](#open-questions-explicit)
- [Definition of done](#definition-of-done)
- [Next steps](#next-steps)

## Objective / decision
**Objective:** Produce one coherent HITL architecture that makes approvals deterministic, storage reliable, and deployments/release pipelines trustworthy.

**Decision needed (from manager):** Confirm/adjust the items in “Manager response (copy/paste)” below so implementation can proceed issue-by-issue without re-litigating fundamentals.

## Manager response (copy/paste)
Please reply by copying this block and filling in blanks.

**Overall**
- Approve this HITL architecture bundle as the contract for Issues #15/#16/#17/#47? (YES/NO): ____

## Decision summary (first-screen)
If you only read one section, read this.
- D1 (Issue #15): Deterministic review decisions with outcomes `approved | rejected | needs_clarification`; first terminal wins; corrections via explicit superseding event.
- D2 (Issue #17/#47): SQLite as MVP source of truth with append-only events + transactional state table projection.
- D3 (Issue #16): Batch Graph Releases only (no online Neo4j writes per approval); approved dataset exported as deterministic bundle w/ manifest + hashes.

**Issue #15 — Review determinism**
- Outcomes enum: `approved | rejected | needs_clarification` (YES/NO): ____
- Notes required for all outcomes (YES/NO): ____
- Skip semantics: Skip == `needs_clarification` (defer/follow-up), reject is separate (YES/NO): ____
- Concurrency/race rule: first terminal decision wins; later attempts return existing; corrections only via explicit tool (YES/NO): ____
- Corrections: append a superseding event with `supersedes_event_id`; never overwrite; keep old decision history queryable (YES/NO): ____

**Issue #17/#47 — Storage + queue**
- MVP storage: SQLite (YES/NO): ____
- Current-state projection: maintain a state table updated transactionally from events (YES/NO): ____
- Queue semantics for MVP: idempotency only (no claim/lease) (YES/NO): ____
- `needs_clarification` escalation after 30 days to fleet management team manager (notify only vs state change?): ____

**KG policy**
- KG updates only when terminal decision recorded (`approved` or `rejected`) (YES/NO): ____
- KG application model: batch Graph Releases (no online Neo4j writes per approval in MVP) (YES/NO): ____
- Rejections should be persisted as negative context/evidence (not just dropped) (YES/NO): ____

**Release artifact (approved dataset export)**
- Export format: zipped bundle with `manifest.json` + per-record JSON + hashes (YES/NO): ____

**Issue #16 — Environments (minimum semantics to lock, even if target is TBD)**
- v1 deployment target: container vs serverless vs VM/systemd: ____
- beta/pilot/prod definition (separate envs vs namespaces): ____
- Minimum environment semantics:
  - Beta: internal dev/testing; can tolerate downtime; manual deploy OK.
  - Pilot: limited stakeholders; rollback expectation defined.
  - Prod: enterprise; minimize downtime; fast rollback required.
  Approve these semantics (YES/NO): ____

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

### HITL E2E diagram (conceptual)
```
                 +-------------------+
                 |  Ingest / Capture |
                 |  (agent + tools)  |
                 +---------+---------+
                           |
                           | submission (schema_versioned)
                           v
                 +-------------------+
                 | SQLite (source of |
                 | truth for MVP)    |
                 | - events (append) |
                 | - state (current) |
                 +----+---------+----+
                      |         |
                      |         | queue views
                      |         v
                      |   +-----------+
                      |   | Operator  |
                      |   | review UI |
                      |   +-----+-----+
                      |         |
                      |         | decision event:
                      |         | approved/rejected/
                      |         | needs_clarification
                      |         v
                      |   +-----------+
                      |   | Follow-up |
                      |   | (clarify) |
                      |   +-----+-----+
                      |         |
                      +---------+
                           |
                           | approved dataset export
                           v
                 +-------------------+
                 | Release pipeline  |
                 | (CI/CD + KG build)|
                 +---------+---------+
                           |
                           | deploy snapshot
                           v
                 +-------------------+
                 | Neo4j Aura (KG)   |
                 +-------------------+
```

### Key invariants
- **Tool-boundary truth:** approvals/rejections are persisted only by validated server-side tool calls (never inferred from prose).
- **Deterministic decisions:** decisions are enum-based, machine-parseable, and idempotent.
- **Append-only history:** we do not rewrite history; when we need to add or correct information, we append a new event/record that supersedes prior records.
- **Write-once reviewed artifacts:** no silent overwrite; correction flows must be explicit.
- **Versioned records:** every HITL record has a `schema_version`.
- **Provenance completeness:** every submission includes who touched it, where it is in the pipeline, and the relevant information for every step up to the current step.
- **Production seam for identity/auth:** operator display fields are not security; in prod, principal identity should be derived from the environment (e.g., employee id from auth/logs) and only simulated via required fields in MCP/tooling (name + role for MVP).

---

## Decisions to lock (contract)

### D1) Decision contract (Issue #15)
**Persisted outcomes:** `approved | rejected | needs_clarification` (lowercase enums).

### Review state machine (MVP)
```
            +-----------+
            |  pending  |
            +-----+-----+
                  |
        +---------+----------+
        |                    |
        v                    v
+---------------+    +----------------------+
|  approved     |    | needs_clarification |
| (terminal)    |    | (non-terminal)      |
+---------------+    +----------+-----------+
                               |
                               | clarification_provided
                               v
                         +-----------+
                         |  pending  |
                         +-----------+

pending -> rejected (terminal) is also allowed.
```

**Skip semantics:** “Skip” means **needs_clarification** (persisted), not “reject.”
- Rationale: in this product, ambiguity is common and must be tracked; “skip” is a defer/follow-up state.
- `needs_clarification` MUST include a reviewer-authored `question` (what is ambiguous / what input is needed).
- `needs_clarification` is **non-terminal**; it does not admit data into the canonical approved dataset.

**Notes policy:** notes are **required for all outcomes**.
- `approved` → notes required (justification/provenance for KG admission)
- `rejected` → notes required (actionable reason)
- `needs_clarification` → notes required + question required

**Idempotency + corrections (resolve “reviewed once” vs “superseding”):**
- **Terminal decision is write-once:** the first terminal decision event (`approved` or `rejected`) “wins” for a given `submission_id`.
- **Repeat terminal attempts are idempotent:** if a terminal decision already exists, repeated calls return the existing terminal decision (no duplicates, no overwrite).
- **Corrections are explicit:** a correction is a *new* event (e.g., `decision_supersedes`) created only by a dedicated correction tool/action.
  - It MUST reference the prior terminal decision event id (`supersedes_event_id`).
  - It produces a *new* terminal decision event id as the active decision.
- **History is preserved:** prior decisions remain queryable for audit/context (and for KG provenance).

**Race behavior (concurrent reviews):**
- If two reviewers attempt terminal decisions concurrently, the system accepts **one** (first write wins) and the other receives the already-recorded terminal decision.
- Concurrency control mechanism (SQLite MVP): transaction + unique constraint on `(submission_id, is_terminal_active)` or equivalent, enforced by the server/tool boundary.

### D2) Storage format + schema evolution (Issues #17 + #47)

### Storage model (SQLite MVP)
```
+------------------+
| hitl_events      |   append-only audit truth
|------------------|
| event_id (PK)    |
| submission_id    |
| event_type       |  submitted / approved / rejected /
| created_at_ms    |  needs_clarification / clarification_provided /
| actor_*          |  supersedes
| notes            |
| event_json       |
+--------+---------+
         |
         | (projection)
         v
+------------------+
| hitl_state       |   current queue state
|------------------|
| submission_id PK |
| current_state    |  pending / needs_clarification / approved / rejected
| updated_at_ms    |
| ...              |
+------------------+
```

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

**KG application model (MVP contract): batch releases (not online writes)**
- The KG is updated only via a **batch “Graph Release”** build + deploy.
- No direct/online writes to Neo4j on each approval in the MVP.
  - Rationale: reproducibility + audit + rollback. (Online writes can be added later.)

**Artifact model:** Approved HITL is treated as a **versioned dataset** (exportable + checksummed) that CI/CD can consume deterministically.

**Release + rollback expectation:**
- Deployments must be attributable (who/what/where) and reversible.
- For Neo4j Aura in prod: prefer blue/green cutover; rollback is a fast URI/secret flip.

---

## Definition of done
This architecture bundle is “done” when:
- the D1/D2/D3 contract sections are ratified, and
- each of #15/#16/#17/#47 references this doc as the shared contract.

Implementation then proceeds in small PRs per issue.

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

   Example release artifact:
   ```
   approved_hitl_release_<date>__<gitsha>.zip
     manifest.json
     records/
       <submission_id_1>.json
       <submission_id_2>.json
     metrics.json   (optional)
   ```

   Reproducibility rules (so the same inputs yield the same artifact):
   - `manifest.json` MUST be deterministic:
     - stable key ordering
     - records listed in lexicographic order by `submission_id`
     - include `sha256` for each record file and for the full bundle
   - record JSON serialization MUST be canonical (no nondeterministic whitespace/ordering).
   - zip creation MUST be deterministic:
     - stable file ordering
     - normalized timestamps (or omitted)

---

## Next steps
1) Merge this plan PR.
2) Add a short comment to issues #15/#16/#17/#47 linking to this plan PR as the architecture contract.
3) Proceed with implementation PRs in small slices, using these locked decisions as the guardrails.
