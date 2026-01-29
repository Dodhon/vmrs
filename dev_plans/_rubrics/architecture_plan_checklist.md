# Architecture plan checklist (rubric)

Use this checklist when writing or reviewing architecture plans under `dev_plans/`.

## Core rubric (keep plans scannable)
- [ ] **Objective + scope + non-goals** are explicit in the first section.
- [ ] **Decision contract** is explicit: which decisions must be locked to proceed.
  - Example (generic): Decision group A = workflow semantics; Decision group B = storage truth; Decision group C = release/deploy semantics.
- [ ] **Current vs proposed** is explicit for any interface/schema/protocol you are changing.
  - Example: “current tool schema supports approved/rejected; proposed workflow adds needs_clarification as non-terminal via event/state until schema bump.”
- [ ] If there is a workflow, a **state machine** is included and distinguishes:
  - terminal outcomes vs non-terminal states
  - correction/supersede semantics (append-only history)
- [ ] **Determinism + reproducibility** rules are stated for any exported/release artifact.
  - Example: canonical JSON serialization, stable ordering, deterministic zip creation, per-record hashes.
- [ ] **Well-Architected (WAF-lite) non-functional posture** is recorded (short; seams allowed):
  - [ ] **Security / privacy / compliance**: principals (who can do what), access boundaries, retention/redaction posture (TBD allowed).
  - [ ] **Reliability**: idempotency, failure modes, backup/restore, rollback path.
  - [ ] **Operational excellence**: observability fields, runbooks, operational ownership.
  - [ ] **Performance**: scalability assumptions, indexing/latency expectations, contention points.
  - [ ] **Cost**: cost posture for MVP, triggers to graduate to heavier infrastructure.
- [ ] **TBD list** is explicit, with a clear resolution path (who decides + where it will be updated).

## Approval-velocity add-on (optional but recommended)
- [ ] Include a short “fast path” approval block (few YES/NO questions) when the plan needs manager sign-off.
  - Example: “Approve direction?”, “Approve decision contract?”, “Approve storage approach?”, “Approve release model?”
