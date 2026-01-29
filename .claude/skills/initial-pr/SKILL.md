---
name: initial-pr
description: Create the initial branch + repo-grounded dev plan + PR draft for a GitHub issue (vmrs).
---

# Initial PR skill (issue → recon → branch → plan → PR draft)

## When to use this skill (critical)
Use this skill **only** when starting work on a **new issue from scratch**:
- No existing PR already tracks the issue
- No existing branch already exists for the issue

If the issue already has a PR/branch, **do not** use this skill to create a new branch/plan/PR draft.
Instead: resume the existing branch/PR and update it.

## Inputs (collect first)
- Issue number: `<N>` (e.g. `18`)
- Repo: `Dodhon/vmrs`

## Reference (GitHub CLI)
For repo-specific `gh` conventions and troubleshooting, read: `.claude/skills/github-cli-workflow/SKILL.md`.

## 0) Preflight: confirm this is a “new issue”
Recommended checks:
```bash
# Is there already a PR tied to this issue?
gh pr list --repo Dodhon/vmrs --state all --search "<N>"

# Do we already have a branch for this issue?
git fetch origin
git branch -a | grep -E "issue/<N>-|issue/<N>\\b|<N>-"
```

## 1) Repo recon (required for plan PRs)
Goal: ensure the plan reflects **current reality** (avoid proposing duplicate CI, wrong entrypoints, etc.).

Minimum recon:
```bash
# Workflows / CI / automation
ls -la .github/workflows || true

# Existing plans (look for prior decisions)
ls -la dev_plans | sed -n '1,120p'

# Locate likely relevant code paths
ls -la mcp src tests "interface prompts" 2>/dev/null || true
```

Record the results in the plan as a **“Current repo state (as of plan creation)”** section with concrete file references.

## 2) Create a new branch
```bash
git fetch origin
git checkout main
git pull --ff-only
git checkout -b "<branch-name>"
```

## 3) Draft a plan (MUST follow `.claude/skills/planning/SKILL.md`)
### Create a plan file in `dev_plans/`
Create a new plan markdown file under `dev_plans/`.

**Required sections (minimum bar):**
- Links (Issue + key repo files)
- Goal + Non-goals
- **Current repo state (repo-grounded)** (from Step 1)
- Proposed approach + decision gates
- Work breakdown + validation plan

### Gather issue context (recommended)
Use `gh` to pull the issue description/comments.

## 4) Create and publish a draft PR based on the plan (required)
- Use the repo PR template (minimum bar) as a checklist.
- PR body must include **Related: #<N>** (or **Fixes/Closes #<N>** only when you intend auto-close).

Create a draft PR immediately after the plan is written:
```bash
gh pr create --repo Dodhon/vmrs --draft \
  --title "Plan: <short title> (Issue #<N>)" \
  --body-file <path-to-body-file>
```

Notes:
- Do **not** create a ready-for-review PR without approval.
