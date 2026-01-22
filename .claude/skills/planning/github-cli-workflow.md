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

## Backlog Project (v2)
- Project URL: `https://github.com/users/Dodhon/projects/1`
- Repo automation: `.github/workflows/add-to-project.yml`
- Secret required: `ADD_TO_PROJECT_PAT` (classic PAT scopes recommended: `project` + `repo`/`public_repo`)

### List projects / fields
```bash
gh project list --owner Dodhon
gh project field-list 1 --owner Dodhon
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
  - Fix: pin to a published tag (example: `actions/add-to-project@v1.0.2`).
- **“Resource not accessible by personal access token”**
  - Fix: use a **classic PAT** with `project` + `repo` (or `public_repo`) and update secret:
    - `gh secret set ADD_TO_PROJECT_PAT --repo Dodhon/vmrs`
- **Workflow doesn’t run at all**
  - Ensure workflow is on **default branch** (`main`) and triggered event matches (issues `opened`/`reopened`).

## Conventions
- **Industry standard flow**: issue → branch → PR → merge → issue auto-closes.
- Use closing keywords in PR body: `Fixes #123`, `Closes #123`, `Resolves #123`.

