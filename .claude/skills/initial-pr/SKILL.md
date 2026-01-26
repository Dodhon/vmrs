---
name: initial-pr
description: Create the initial branch + dev plan + PR draft for a GitHub issue (vmrs). 
---

# Initial PR skill (issue → branch → plan → PR draft)

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

## 1) Create a new branch

```bash
git fetch origin
git checkout main
git pull --ff-only
git checkout -b "<branch-name>"
```

## 2) Draft a plan (MUST follow `.claude/skills/planning/SKILL.md`)

### Create a plan file in `dev_plans/`
Create a new plan markdown file under `dev_plans/` (name is up to you).

### Gather issue context (recommended)
Use `gh` to pull the issue description/comments (see `.claude/skills/github-cli-workflow/SKILL.md`).

Also check the Backlog Project item `Status` for the issue/PR (project fields don’t show up in `gh issue list` / `gh pr list`).

## 3) Create a draft PR based on the plan (allowed)

Use the PR drafting guidance/template in `.claude/skills/github-cli-workflow/SKILL.md` and ensure the PR is derived from (and links to) the plan you wrote in Step 2.

Notes:
- It’s **OK to create a draft PR** (use `gh pr create --draft`).
- Do **not** create a ready-for-review PR without approval.
