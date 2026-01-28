# CLAUDE.md (VMRS)

Quick repo facts and conventions for AI assistants working in this repository.

## Planning
- Architecture/design plans live in `dev_plans/`.
- Architecture plan rubric: `dev_plans/_rubrics/architecture_plan_checklist.md`.

## Writing standards (short)
- Objective first.
- Make decisions explicit.
- Prefer deterministic, audit-friendly artifacts when producing deployable state.

## Workflow semantics (when applicable)
- Distinguish terminal decisions vs non-terminal workflow states.
- Corrections are append-only and explicitly supersede prior events.

## PR hygiene
- Link the plan file from the PR body when the PR is a planning PR.
- Avoid auto-closing keywords unless you intend the merge to close the issue.
