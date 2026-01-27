# Plan: Issue #16 — CI/CD pipeline for deploys + rollbacks (beta/pilot/prod)

## Links
- Issue #16: https://github.com/Dodhon/vmrs/issues/16

## Goal
Create a minimal but solid CI/CD foundation that supports:
- automated CI on PRs
- environment deploys (beta → pilot → prod)
- fast rollback to last-known-good
- reproducible artifacts (at least by commit SHA)

## Non-goals (for this issue)
- Perfect production infra design (we’ll pick a pragmatic initial target)
- Complex secrets rotation / SSO / compliance hardening
- Full IaC rewrite (Terraform, etc.) unless required

## Key decisions (need manager input)
1) Deployment target (pick one for v1):
- A) Container image (recommended default)
- B) Serverless function
- C) VM + systemd

2) Environment model:
- A) Separate environments (beta/pilot/prod) with clearly separated secrets
- B) Single environment with namespaces (only if infra forces it)

3) Release strategy:
- A) Trunk-based + tagged releases
- B) Release branches

## Current repo state (as of plan creation)
- GitHub Actions already exists:
  - `.github/workflows/ci.yml` runs on PRs and pushes to `main`.
    - Sets up Python 3.12
    - Installs `pytest`
    - Checks the HITL schema prompt excerpt is up to date (`python -m src.hitl_schema --check-excerpt "interface prompts/hitl_schema_excerpt.txt"`)
    - Runs `pytest -q`
  - `.github/workflows/add-to-project.yml` auto-triages issues/PRs into the Project (v2).
- There is **no CD/deploy workflow** yet.
- The repo is Python-first (see `requirements.txt` and the README `python3 -m venv ...` setup).

## Proposed approach (recommended v1)
- Build on the existing CI (`.github/workflows/ci.yml`) rather than replace it.
- Extend CI minimally to include any deterministic lint/format checks you adopt (optional).
- Add CD as separate workflows (manual first):
  - workflow_dispatch deploy to beta
  - promotion job: beta → pilot → prod
- Define rollback as “redeploy previous known-good artifact SHA”.
- Artifact choice (container vs other) remains a decision gate; default recommendation is container image tagged by commit SHA.

## Work breakdown
E1) Repo recon
- Identify runtime components that need deploy (MCP servers? API? services?)
- Identify language/toolchain (python node) and existing test entrypoints

E2) CI workflow
- Add GitHub Actions workflow for PR checks
- Enforce required checks in branch protection (if desired)

E3) Artifact build
- Decide artifact format (container vs package)
- Produce artifact on main merges (and optionally PRs)

E4) CD workflows (beta/pilot/prod)
- Add deploy workflows with manual triggers
- Document required secrets and environment separation

E5) Rollback procedure
- Document rollback steps
- Validate rollback is fast + repeatable

## Validation / acceptance criteria
- [ ] CI runs on PRs and blocks merge on failure
- [ ] Deploy-to-beta can be executed via GH Actions
- [ ] Rollback can redeploy a previous known-good artifact within an agreed time window
- [ ] Environments + secrets separation documented
- [ ] Artifacts are identifiable (at minimum commit SHA)

## Open questions
- What is the intended production host for the agent/plugin backend?
- Do we need staging data / Neo4j migration strategy in v1 CD?
