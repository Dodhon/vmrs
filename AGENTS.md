# AGENTS.md (VMRS)

This file documents repo-local agent workflow conventions for VMRS.

## Planning (architecture/design)
- Put architecture/design plans under `dev_plans/`.
- Use the rubric: `dev_plans/_rubrics/architecture_plan_checklist.md`.
- Prefer plan docs that explicitly lock the key decisions (workflow semantics, storage truth, release/deploy semantics).
- When interfaces/schemas change: include a clear "current vs proposed" section.

## Repo grounding
Before drafting an architecture plan or making non-trivial changes:
- Scan `README.md`, relevant existing `dev_plans/`, and relevant code paths.
- Cite file paths/symbols in plans and PR descriptions when possible.

## HITL / workflow conventions (summary)
- Decisions are tool-boundary truth (no decision inferred from prose).
- Prefer append-only event history with explicit supersedes/corrections.
- Prefer deterministic, auditable release artifacts when producing KG updates.
