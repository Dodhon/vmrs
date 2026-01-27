# Plan: Issue #16 — CI/CD pipeline for deploys + rollbacks (beta/pilot/prod)

## 0. Executive Summary
We will define and implement a minimal CI/CD system for VMRS that (1) runs deterministic checks on every PR, (2) produces an immutable deploy artifact (at minimum tagged by commit SHA), (3) supports manual deployments to beta/pilot/prod with clear promotion gates, and (4) supports rollback by redeploying a prior known-good artifact. The first step is to confirm the deployable unit and deployment target; everything else follows from that decision.

**Ask (decisions needed to proceed):**
- Pick deployment target for v1 (container vs serverless vs VM+systemd).
- Define what “beta / pilot / prod” concretely mean (separate hosts/projects vs same host + namespaces).

## 1. Introduction / Purpose
- Purpose: specify an actionable CI/CD plan (including rollback) suitable for beta→pilot→prod.
- Audience: repo maintainers and whoever will operate deployments.
- Decision enabled: choose the v1 deployment target + environment model so implementation can begin.

## Links
- Issue #16: https://github.com/Dodhon/vmrs/issues/16

## Goal
Create a minimal but solid CI/CD foundation that supports:
- automated CI on PRs
- environment deploys (beta → pilot → prod)
- fast rollback to last-known-good
- reproducible artifacts (at least by commit SHA)

## Functional requirements
FR1. CI runs on every PR and on merges to `main`.
FR2. CI produces a clear pass/fail signal and blocks merge when failing (via branch protection or an equivalent policy).
FR3. A deploy workflow can deploy a specific commit SHA to a named environment (beta/pilot/prod).
FR4. A rollback workflow can redeploy a prior known-good artifact (by SHA/tag) to the same environment.
FR5. Deploy workflows record “who deployed what where” (at minimum in GitHub Actions run history).

## Non-functional requirements
NFR1. Artifacts are immutable and identifiable (commit SHA tagging minimum).
NFR2. Rollback is fast and repeatable (target: operator can roll back within minutes once a bad deploy is detected).
NFR3. Environments are isolated by secrets and configuration; beta cannot access prod secrets.
NFR4. Deploy steps are deterministic and documented (no manual hidden steps required for success).

## Architecture diagram (CI/CD topology)
```
Developer PR
   |
   v
GitHub Actions CI (tests, checks)
   |
   +--> (on main) build artifact tagged with SHA
                 |
                 v
            Artifact registry
                 |
                 +--> Deploy beta  (manual)
                 |
                 +--> Promote pilot (manual gate)
                 |
                 +--> Promote prod  (manual gate)

Rollback: select prior SHA -> redeploy to env
```

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
E1) Repo recon (fill in what we’re actually deploying)
- Identify runtime components that need deploy (MCP servers? API? services?)
- Identify language/toolchain (python node) and existing test entrypoints

E2) CI workflow
- Confirm CI is the required status check for branch protection
- Add deterministic checks you want long-term (optional: lint/format)

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
