---
name: github-cli-workflow
description: Standardize GitHub CLI (gh) workflows for this repo: create/triage issues, manage the Backlog Project (v2), create branches/PRs, link PRs to issues (Fixes #), and troubleshoot Actions/Projects automation failures.
---

# GitHub CLI workflow (vmrs)

## Quick start (most common)

### Create an issue (goes to Backlog Project via automation)
```bash
gh issue create --repo Dodhon/vmrs --title "..." --body "..."
```

### Create a PR and auto-close an issue on merge
1) Create a branch, push commits
2) Create PR:
```bash
gh pr create --repo Dodhon/vmrs --base main --title "..." --body "Fixes #<issue-number>"
```

### PR body template (plan-driven)
Use this when your work starts with a plan doc in `dev_plans/` (see `.claude/skills/planning.md` for plan requirements).

```text
Fixes #<issue-number>

## Summary
- <1–3 bullets mapping to plan Goals>

## Plan
- **Plan doc**: `dev_plans/<plan>.md`
- **Key decisions**:
  - <link to plan section(s)>

## Test plan
- [ ] <how success metrics will be validated>

## Notes / rollout
- <sequencing / flags / backwards-compat (if relevant)>
```

## Backlog Project (v2)
- Project URL: `https://github.com/users/Dodhon/projects/1`
- Repo automation: `.github/workflows/add-to-project.yml`
- Secret required: `ADD_TO_PROJECT_PAT` (PAT must have Projects v2 access + repo access for assigning issues)

### See issue “Status” (Project field)
Issue status (e.g. `Status=Todo|Done`) lives on the **Project item**, not on the issue itself—so use `gh project ...` to see it.

```bash
# List project items with their current Status
gh project item-list 1 --owner Dodhon --limit 200 --format json -q '.items[] | {number: .content.number, title: .content.title, status: .status}'
```

### List projects / fields
```bash
gh project list --owner Dodhon
gh project field-list 1 --owner Dodhon
```

### Label → Project field mapping (used by automation)
- **Required**: Project single-select field `Status` with options `Todo` and `Done`
- **Optional (best-effort)**:
  - Label `area:<AREA_OPTION>` sets Project single-select field `Area`
  - Label `priority:P0|P1|P2` sets Project single-select field `Priority`
  - Project text field `Importance` is set to `P0|P1|P2` (defaults to `P2` when unlabeled)

### Manual backfill (one-time / safe to re-run)
This adds all currently-open issues + PRs to the Backlog project (idempotent) and sets baseline `Status=Todo`.

```bash
gh workflow run add-to-project.yml --repo Dodhon/vmrs
```

Dry-run (no mutations):

```bash
gh workflow run add-to-project.yml --repo Dodhon/vmrs -f dry_run=true
```

## Triage (labels + milestones)

### Labels
```bash
gh label list --repo Dodhon/vmrs --limit 200
gh label create "triage" --repo Dodhon/vmrs --color "FBCA04" --description "Needs triage" || true
```

### Apply labels / assign
```bash
gh issue edit <n> --repo Dodhon/vmrs --add-label "triage,type:feature,area:hitl"
gh issue edit <n> --repo Dodhon/vmrs --add-assignee "@me"
```

## Actions troubleshooting (auto-add workflow)

### Check runs
```bash
gh workflow list --repo Dodhon/vmrs
gh run list --repo Dodhon/vmrs --workflow add-to-project.yml --limit 10
gh run view --repo Dodhon/vmrs <run-id> --log
```

### Known failure modes + fixes
- **Action tag not found**: error like “unable to find version”
  - Fix: pin to a published tag.
- **“Resource not accessible by personal access token”**
  - Fix: ensure the PAT has Projects v2 access and repo access, then update secret:
    - `gh secret set ADD_TO_PROJECT_PAT --repo Dodhon/vmrs`
- **Workflow doesn’t run at all**
  - Ensure workflow is on **default branch** (`main`) and triggered event matches (issues/PRs `opened`/`reopened`/`closed`).
- **Workflow fails with missing `Status` / `Todo` / `Done`**
  - Fix: in the Backlog Project, ensure the `Status` field exists (single-select) and contains options named exactly `Todo` and `Done`.

## Conventions
- **Industry standard flow**: issue → branch → PR → merge → issue auto-closes.
- Use closing keywords in PR body: `Fixes #123`, `Closes #123`, `Resolves #123`.

