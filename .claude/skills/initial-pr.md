---
name: initial-pr
description: Create the initial branch + dev plan + PR draft for a GitHub issue (vmrs). 
---

# Initial PR skill (issue → branch → plan → PR draft)

## Inputs (collect first)
- Issue number: `<N>` (e.g. `18`)
- Repo: `Dodhon/vmrs`

## Reference (GitHub CLI)
For repo-specific `gh` conventions and troubleshooting, read: `.claude/skills/github-cli-workflow.md`.

## 1) Create a new branch

```bash
git fetch origin
git checkout main
git pull --ff-only
git checkout -b "<branch-name>"
```

## 2) Draft a plan (MUST follow `.claude/skills/planning.md`)

### Create a plan file in `dev_plans/`
Create a new plan markdown file under `dev_plans/` (name is up to you).

### Gather issue context (recommended)
Use `gh` to pull the issue description/comments (see `.claude/skills/github-cli-workflow.md`).

## 3) Draft a PR based on the plan (do not create it without approval)

Use the PR drafting guidance/template in `.claude/skills/github-cli-workflow.md` and ensure the PR is derived from (and links to) the plan you wrote in Step 2.
