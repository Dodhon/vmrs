# HITL Architecture Review (Bundle): Issues #15, #16, #17, #47

## Table of contents
- [Objective](#objective)
- [Scope](#scope)
- [Why these are bundled](#why-these-are-bundled)
- [Proposed architecture (high level)](#proposed-architecture-high-level)
- [System invariants (non-negotiables)](#system-invariants-non-negotiables)
- [Well-Architected (AWS/GCP) considerations](#well-architected-awsgcp-considerations)
- [Contract decisions to lock (D1/D2/D3)](#contract-decisions-to-lock-d1d2d3)
- [Open questions (explicit, non-blockers)](#open-questions-explicit-non-blockers)
- [Definition of done](#definition-of-done)
- [Next steps](#next-steps)
- [Manager response (copy/paste)](#manager-response-copypaste)

## Objective
Produce one coherent HITL architecture that makes decisions deterministic, storage reliable, and KG releases auditable/rollbackable.

## Scope
This doc bundles and aligns:
- **#15** Deterministic, schema-validated HITL review decisions
- **#17** HITL storage format + schema evolution
- **#47** Evaluate stateful storage for HITL status/queue
- **#16** CI/CD + release/rollback model for deploying the knowledge graph

## Why these are bundled
These issues define one coupled contract:
- what a decision *is*
- where HITL truth lives
- how approved HITL becomes a release input for KG builds

## Proposed architecture (high level)

### Canonical flow
1) Capture creates a pending submission (schema-versioned).
2) Review records an explicit decision via a tool call (tool-boundary truth).
3) Approved HITL is exported as a versioned dataset artifact.
4) CI/CD builds a Graph Release from approved inputs and deploys it to Neo4j (rollbackable).

### HITL E2E diagram (conceptual)

```text
                 +-------------------+
                 |  Ingest / Capture |
                 |  (agent + tools)  |
                 +---------+---------+
                           |
                           | submission (schema_versioned)
                           v
                 +-------------------+
                 | SQLite (MVP truth)|
                 | events (append)   |
                 | state (current)   |
                 +----+---------+----+
                      |         |
                      |         | queue views
                      |         v
                      |   +-----------+
                      |   | Operator  |
                      |   | review UI |
                      |   +-----+-----+
                      |         |
                      |         | decision event
                      |         v
                      |   +-----------+
                      |   | Follow-up |
                      |   | clarify   |
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

## System invariants (non-negotiables)
- **Tool-boundary truth:** no decision inferred from prose.
- **Append-only history:** do not rewrite records; corrections are new events.
- **Provenance completeness:** each submission includes who touched it, pipeline step, and relevant info up to that step.
- **Production identity seam:** in prod use employee id (from auth/logs); MVP stores name + role.

## Well-Architected (AWS/GCP) considerations
This section is intentionally short: it records the non-functional posture for MVP and the seams we will harden as we move toward enterprise deployment.

Principals (who can do what)
- Principal: an authenticated actor that can read/submit/review/correct HITL items (operator, agent, or system).
- In MVP, principal identity is recorded as name + role (and optional team). In prod, the authoritative principal identifier is employee id from auth/logs.
- Authorization (policy):
  - Only authorized principals can record terminal decisions (approved/rejected).
  - Only authorized principals can create correction/superseding events.

Security, privacy, compliance
- HITL notes/context may contain sensitive operational/vendor data.
- Redaction policy: TBD (define what can be stored in notes/context, what must be masked, and retention windows).
- Integrity: approved dataset export is tamper-evident via deterministic manifest + per-record hashes. (Optional later: sign artifacts.)

Reliability
- Idempotency: retries must not create duplicate decisions; request_id is used as an idempotency key for tool retries.
- Failure modes (MVP): define behavior for SQLite locked, disk full, and partial export failure (retry-safe, fail loud).
- Recovery: define backup/restore for SQLite (frequency + restore steps) and confirm Graph Release rollback path (redeploy prior known-good artifact).

Operational excellence
- Observability: every event/decision/correction includes actor identity fields and timestamps; exports include manifest metadata (counts, hashes, inputs).
- Runbooks: document how to re-run export, backfill state projection, and run escalation for stale needs_clarification items.

Performance/scalability
- MVP boundaries: assume one writer to SQLite and short transactions; enable WAL mode and set busy timeout/retry.
- Indexing: at minimum index submission_id, current_state, created_at_ms, and active terminal decision pointers.

Cost optimization
- SQLite + batch Graph Releases minimize operational overhead for MVP.
- Trigger to migrate to Postgres: multiple service instances writing concurrently, stronger HA requirements, or sustained write contention.

Sustainability (optional)
- Prefer batch releases and minimal always-on infrastructure in MVP; revisit once volume and uptime targets are defined.

## Contract decisions to lock (D1/D2/D3)

### D1. Review decision contract (Issue #15)

#### Current schema vs proposed schema (clarifies needs_clarification)
- Current HITL schema excerpt supports terminal review outcomes: **approved**, **rejected**.
- Proposed architecture adds **needs_clarification** as a workflow state (non-terminal) for follow-up.
  - In the MVP, needs_clarification is **not** a terminal review decision.
  - It is recorded as an **event/state** and returns to **pending** once feedback is received.

#### Semantics
- Terminal outcomes enum: **approved**, **rejected**.
- Non-terminal state: **needs_clarification**.
- Skip semantics: Skip means **needs_clarification** (defer/follow-up). Reject is separate.
- Notes: required for all outcomes/states.

#### Terminal decision rule
- The first terminal decision (approved or rejected) wins for a submission_id.
- Subsequent terminal attempts return the existing terminal decision (idempotent).

#### Corrections
- Corrections are explicit and append-only (dedicated correction action/tool).
- Correction event must reference the prior decision event id (`supersedes_event_id`).
- Prior decisions remain queryable for audit and KG provenance.

#### Race behavior
- Concurrent terminal reviews: first write wins; other caller receives the already-recorded terminal decision.

#### Review state machine (MVP)

```text
            +-----------+
            |  pending  |
            +-----+-----+
                  |
        +---------+----------------+
        |                          |
        v                          v
approved_or_rejected (terminal)  needs_clarification (non-terminal)
                                  |
                                  v
                     clarification_provided -> pending

Terminal note:
- approved_or_rejected is a terminal bucket in this diagram.
- The system still records the specific terminal outcome (approved vs rejected), and rejected decisions carry negative context/evidence.
```

### D2. Storage + queue (Issues #17 and #47)
- MVP storage: **SQLite**.
- Storage model:
  - `hitl_events`: append-only audit truth
  - `hitl_state`: transactional projection for current queue state

#### SQLite tables (conceptual)

```text
+------------------------+
| hitl_submissions       |  immutable submission payload + provenance
|------------------------|
| submission_id (PK)     |  e.g., HITL-<uuid>
| schema_version         |
| submission_type        |  correction|addition|context|question
| submitted_at_ms        |
| status_initial         |  pending
| submitter_name         |
| submitter_role         |
| submitter_id (opt)     |  employee id in prod
| submitter_team (opt)   |
| vmrs_code              |
| description            |
| context                |
| related_query          |
| target_type (opt)      |
| target_key_json (opt)  |
| targets_json (opt)     |
| context_pack_json (opt)|  enforce <=500 char excerpt inside
| proposed_action (opt)  |
| proposed_payload_json  |
| pipeline_step          |  where in the pipeline this was produced
| source_system (opt)    |  agent/tool/ui name
| source_record_id (opt) |
| pipeline_run_id (opt)  |
| touched_by_json (opt)  |  who/what touched it so far
| submission_hash_sha256 |
| payload_json           |  canonical JSON (full)
+------------+-----------+
             |
             | events
             v
+------------------------+
| hitl_events            |  append-only audit truth
|------------------------|
| event_id (PK)          |
| submission_id (FK)     |
| event_type             |  submitted|needs_clarification|
|                        |  clarification_provided|decision_recorded|
|                        |  decision_supersedes
| created_at_ms          |
| actor_kind             |  operator|agent|system
| actor_name             |
| actor_role             |
| actor_id (opt)         |
| actor_team (opt)       |
| notes                  |  required
| decision_outcome (opt) |  approved|rejected (only for decision_recorded)
| question (opt)         |  required for needs_clarification
| answer (opt)           |  for clarification_provided
| supersedes_event_id    |  required for decision_supersedes
| request_id (opt)       |  idempotency key for tool retries
| link_assertions_json   |  structured KG/MDM link assertions
| event_json             |  canonical JSON (full)
+------------+-----------+
             |
             | projection
             v
+--------------------------------------------------------------+
| hitl_state                                                     |
| current queue state (projection)                               |
|--------------------------------------------------------------|
| submission_id (PK)                                             |
| current_state              pending|needs_clarification|approved|rejected |
| updated_at_ms                                                  |
| active_terminal_event_id (opt)                                 |
| active_decision_outcome (opt)                                  |
| needs_clarification_since_ms (opt)                             |
| escalation_due_at_ms (opt)                                     |
| escalated_at_ms (opt)                                          |
| escalation_target (opt)                                        |
+--------------------------------------------------------------+
```

#### Queue semantics (MVP)
- Idempotency-only (no claim/lease). Assumes low reviewer concurrency. Revisit when duplicate-work becomes a problem.

#### Escalation
- If an item sits in needs_clarification for 30 days, escalate to the fleet management team manager (exact mechanism TBD).

#### MDM identity stance (single-tenant)
- VMRS codes are canonical by value and key for matching.
- Vendors/vendor parts are MDM entities (canonical ids, aliases, merge/supersede).
- Other/none-of-the-above routes to a needs-followup pile for later resolution (likely in-person).

### D3. KG update + release model (Issue #16)
- KG updates only after a terminal decision is recorded (approved or rejected).
- KG application model (MVP): batch Graph Releases only (no online Neo4j writes per approval).
- Rejections are persisted as negative context/evidence (not just dropped).

#### Proposed Neo4j schema extension (future; NOT in MVP)
Goal: show how HITL becomes graph provenance and how MDM mappings can be superseded while preserving history.

Current core (as-is)
- Nodes: System, Assembly, Component, Vendor, VendorPart
- Relationships: Assembly-PART_OF->System; Component-PART_OF->Assembly; Vendor-MANUFACTURES->VendorPart; VendorPart-MAPS_TO->Component

Proposed additions for HITL + MDM (recommended)
- Multiple viable approaches (choose based on query/ops needs):
  - A) Keep MAPS_TO as a relationship and store provenance on the relationship (simpler graph, weaker history model).
  - B) Reify mappings as nodes (recommended for HITL/MDM): HITL attaches to “the mapping” and preserves superseding history.
  - C) Hybrid: keep MAPS_TO edge for fast lookups, but treat the mapping node as source of truth.
- Operational note: subagents can answer questions against canonical graph-only views vs HITL evidence/provenance views.

Proposed relationship summary

```text
System
  ^
  | PART_OF
Assembly
  ^
  | PART_OF
Component  <-- TO_COMPONENT --  VendorPartComponentMapping  -- HAS_MAPPING -->  VendorPart  <-- MANUFACTURES -- Vendor

HITLSubmission -- PROPOSES_MAPPING --> VendorPartComponentMapping
HITLDecisionEvent -- FOR_SUBMISSION --> HITLSubmission
HITLDecisionEvent -- DECIDES_MAPPING --> VendorPartComponentMapping
HITLSubmission / HITLDecisionEvent -- (SUBMITTED_BY/ACTED_BY) --> Actor
HITLDecisionEvent -- SUPERSEDES --> HITLDecisionEvent
```

Rationale
- Reified mapping nodes make it easy to attach approval provenance, rejection reasons, and superseding history.
- Active mapping rule must be explicit:
  - Invariant: VendorPart has 0..1 active mapping at a time.

#### Approved dataset export (release input)
- Format: zipped bundle containing manifest + per-record JSON + hashes.
- At export time, finalize the exact KG changes to apply:
  - the entities and relationships to write
  - the properties on those nodes/edges
  This makes the Graph Release reproducible and auditable (the KG isn’t re-decided at deploy time).
- Reproducibility rules:
  - manifest is deterministic (stable key ordering; records sorted by submission_id)
  - record JSON serialization is canonical
  - zip creation is deterministic (stable file ordering; normalized/omitted timestamps)

Example

```text
approved_hitl_release_<date>__<gitsha>.zip
  manifest.json
  records/
    <submission_id_1>.json
    <submission_id_2>.json
  metrics.json (optional)
```

## Open questions (explicit, non-blockers)
1) Escalation mechanism: notify only vs also change workflow state.
2) Needs-followup pile: exact data shape and resolution workflow for MDM entity creation/merge.
3) Issue #16 minimum env semantics: confirm beta/pilot/prod definitions and rollback expectations (deployment target can remain TBD).

## Definition of done
- D1/D2/D3 above are ratified.
- Issues #15/#16/#17/#47 reference this doc as the contract.
- Implementation proceeds via small PRs per issue.

## Next steps
1) Get manager responses below.
2) Define the redaction policy (TBD): what is allowed in notes/context, what must be masked, and retention windows.
3) Update this doc if needed.
4) Proceed with implementation PRs per issue.

## Manager response (copy/paste)
Please reply by copying this block and filling in blanks.

Fast path
- Approve direction (YES/NO): ____
- Approve D1 (decision contract) (YES/NO): ____
- Approve D2 (SQLite + event log + state projection) (YES/NO): ____
- Approve D3 (batch Graph Releases + deterministic export artifact) (YES/NO): ____

If any NO above, fill details below

Overall
- Approve this HITL architecture bundle as the contract for Issues 15/16/17/47? (YES/NO): ____

Issue 15 review determinism
- Terminal outcomes enum is approved/rejected; needs_clarification is a non-terminal state that returns to pending after feedback (YES/NO): ____
- Notes required for all outcomes/states (YES/NO): ____
- Skip means needs_clarification (defer/follow-up) and reject is separate (YES/NO): ____
- Concurrency rule: first terminal wins; later attempts return existing; corrections only via explicit tool (YES/NO): ____
- Corrections: append superseding event referencing supersedes_event_id; never overwrite; keep history queryable (YES/NO): ____

Issues 17 and 47 storage and queue
- MVP storage is SQLite (YES/NO): ____
- Maintain hitl_state table projection (YES/NO): ____
- MVP queue uses idempotency only (no claim/lease) (YES/NO): ____
- needs_clarification escalation after 30 days to fleet management manager; mechanism (notify only vs state change): ____

KG policy
- KG updates only when terminal decision recorded (YES/NO): ____
- MVP KG application model is batch Graph Releases (no online writes per approval) (YES/NO): ____
- Rejections persist as negative context/evidence (YES/NO): ____

Approved dataset export
- Export is deterministic zip bundle with manifest + per-record JSON + hashes (YES/NO): ____

Issue 16 minimum env semantics (even if deployment target is TBD)
- Beta definition: internal dev/testing; can tolerate downtime; manual deploy OK (YES/NO): ____
- Pilot definition: limited stakeholders; rollback expectation defined (YES/NO): ____
- Prod definition: minimize downtime; fast rollback required (YES/NO): ____
- v1 deployment target (container vs serverless vs VM/systemd): ____
- beta/pilot/prod model (separate envs vs namespaces): ____
