HITL ARCHITECTURE REVIEW (BUNDLE): ISSUES 15, 16, 17, 47

Objective
Produce one coherent HITL architecture that makes decisions deterministic, storage reliable, and KG releases auditable/rollbackable.

Scope (what this covers)
- Issue 15: deterministic, schema-validated HITL review decisions
- Issue 17: HITL storage format + schema evolution
- Issue 47: whether HITL status/queue needs stateful storage
- Issue 16: CI/CD + release/rollback model for deploying the knowledge graph

Why these are bundled
These issues define one coupled contract: (a) what a decision is, (b) where truth lives, and (c) how approved HITL becomes a release input for the KG.

Proposed architecture (high level)
Canonical flow
1) Capture creates a pending submission (schema_versioned).
2) Review records an explicit decision via a tool call (tool-boundary truth).
3) Approved HITL is exported as a versioned dataset artifact.
4) CI/CD builds a Graph Release from approved inputs and deploys it to Neo4j (rollbackable).

HITL E2E diagram (conceptual)

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

System invariants (non-negotiables)
- Tool-boundary truth: no decision inferred from prose.
- Append-only history: do not rewrite records; corrections are new events.
- Provenance completeness: each submission includes who touched it, pipeline step, and relevant info up to that step.
- Production identity seam: in prod use employee id (from auth/logs); MVP stores name + role.

Contract decisions to lock (D1/D2/D3)

D1. Review decision contract (Issue 15)
- Outcomes enum: approved, rejected, needs_clarification.
- Skip semantics: Skip means needs_clarification (defer/follow-up). Reject is separate.
- Notes: required for all outcomes.
- Terminal decision rule:
  - The first terminal decision (approved or rejected) wins for a submission_id.
  - Subsequent terminal attempts return the existing terminal decision (idempotent).
- Corrections:
  - Corrections are explicit and append-only (dedicated correction action/tool).
  - Correction event must reference the prior decision event id (supersedes_event_id).
  - Prior decisions remain queryable for audit and KG provenance.
- Race behavior:
  - Concurrent terminal reviews: first write wins; other caller receives the already-recorded terminal decision.

Review state machine (MVP)

            +-----------+
            |  pending  |
            +-----+-----+
                  |
        +---------+----------+
        |                    |
        v                    v
    approved (terminal)   needs_clarification (non-terminal)
        |
        v
    rejected (terminal) is also allowed from pending

needs_clarification -> clarification_provided -> pending

D2. Storage + queue (Issues 17 and 47)
- MVP storage: SQLite.
- Storage model:
  - hitl_events: append-only audit truth
  - hitl_state: transactional projection for current queue state

SQLite tables (conceptual)

+------------------+
| hitl_events      |  append-only audit truth
|------------------|
| event_id (PK)    |
| submission_id    |
| event_type       |
| created_at_ms    |
| actor_*          |
| notes            |
| event_json       |
+--------+---------+
         |
         | projection
         v
+------------------+
| hitl_state       |  current queue state
|------------------|
| submission_id PK |
| current_state    |  pending / needs_clarification / approved / rejected
| updated_at_ms    |
| ...              |
+------------------+

Queue semantics (MVP)
- Idempotency-only (no claim/lease). Assumes low reviewer concurrency. Revisit when duplicate-work becomes a problem.

Escalation
- If an item sits in needs_clarification for 30 days, escalate to the fleet management team manager (exact mechanism TBD).

MDM identity stance (single-tenant)
- VMRS codes are canonical by value and key for matching.
- Vendors/vendor parts are MDM entities (canonical ids, aliases, merge/supersede).
- Other/none-of-the-above should route to a needs-followup pile for later resolution (likely in-person).

D3. KG update + release model (Issue 16)
- KG updates only after a terminal decision is recorded (approved or rejected).
- KG application model (MVP): batch Graph Releases only (no online Neo4j writes per approval).
- Rejections are persisted as negative context/evidence (not just dropped).

Approved dataset export (release input)
- Format: zipped bundle containing manifest + per-record JSON + hashes.
- Reproducibility rules:
  - manifest is deterministic (stable key ordering; records sorted by submission_id).
  - record JSON serialization is canonical.
  - zip creation is deterministic (stable file ordering; normalized/omitted timestamps).

Example

approved_hitl_release_<date>__<gitsha>.zip
  manifest.json
  records/
    <submission_id_1>.json
    <submission_id_2>.json
  metrics.json (optional)

Open questions (explicit, non-blockers)
1) Escalation mechanism: notify only vs also change workflow state.
2) Needs-followup pile: exact data shape and resolution workflow for MDM entity creation/merge.
3) Issue 16 minimum env semantics: confirm beta/pilot/prod definitions and rollback expectations (deployment target can remain TBD).

Definition of done
- D1/D2/D3 above are ratified.
- Issues 15/16/17/47 reference this doc as the contract.
- Implementation proceeds via small PRs per issue.

Next steps
1) Get manager responses below.
2) Update this doc if needed.
3) Proceed with implementation PRs per issue.


MANAGER RESPONSE (COPY/PASTE)
Please reply by copying this block and filling in blanks.

Overall
- Approve this HITL architecture bundle as the contract for Issues 15/16/17/47? (YES/NO): ____

Issue 15 review determinism
- Outcomes enum approved/rejected/needs_clarification (YES/NO): ____
- Notes required for all outcomes (YES/NO): ____
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
