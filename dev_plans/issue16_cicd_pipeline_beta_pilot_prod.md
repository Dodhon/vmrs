# Plan: Issue #16 — CI/CD pipeline for deploys + rollbacks + Knowledge Graph releases (beta/pilot/prod)

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

## Executive summary (for manager feedback)
We need a CI/CD + DataOps pipeline that can repeatedly build and deploy both (a) the application and (b) a versioned Neo4j Aura knowledge graph, while safely incorporating VMRS handbook updates, vendor data, HITL approvals, and removals.

This plan proposes a **Graph Release** model (manifest + metrics + loadable snapshot artifact) built in CI (ephemeral Neo4j in Docker), then deployed to Aura environments via import/upload.

Manager input requested (high-signal decisions):
- **Prod graph deploy architecture:** confirm blue/green cutover is the right choice for “no downtime” and confirm the cutover mechanism (app secret flip vs DNS vs router).
- **Beta/pilot graph deploy:** choose whether we accept downtime (in-place overwrite) or standardize on blue/green everywhere.
- **Canonical data sources:** where the “remote canonical” datasets live for handbook/vendor/HITL/removals (repo vs object storage) and what the approval workflow is for HITL.
- **Quality gates:** acceptable rollback time, drift thresholds, and required smoke queries before promotion.

## Goal
Create a minimal but solid CI/CD foundation that supports:
- automated CI on PRs
- environment deploys (beta → pilot → prod)
- fast rollback to last-known-good
- reproducible artifacts (at least by commit SHA)
- **knowledge graph “Graph Releases”** that incorporate:
  - VMRS handbook updates
  - new vendor data
  - new HITL data (local authoring + remote canonical)
  - removals/deprecations
  - observability (lineage + metrics) and rollback

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

## Key decisions (need input)
1) **Application deployment target (non-KG runtime)** (pick one for v1):
- A) Container image (recommended default)
- B) Serverless function
- C) VM + systemd

2) **Environment model**:
- A) Separate environments (beta/pilot/prod) with clearly separated secrets
- B) Single environment with namespaces (only if infra forces it)

3) **Release strategy**:
- A) Trunk-based + tagged releases
- B) Release branches

4) **Knowledge graph backend for MVP**:
- **Neo4j Aura** (confirmed)

5) **Graph deploy/rollback mechanism for Aura**:
- **Prod requirement: no downtime → choose Blue/Green**
  - Maintain *separate Aura instances* (or separate DBs) for “blue” (serving) and “green” (candidate).
  - Deploy = import/upload snapshot into **green**, run smoke tests, then cut over by switching the app’s Neo4j URI/secret (or DNS).
  - Rollback = switch back to the previous URI/secret (fast).
- **Beta/pilot option (if downtime is acceptable): in-place overwrite**
  - Upload/import snapshot into the single target Aura instance (overwrites DB).
  - Simpler + cheaper, but implies deploy downtime during restore/import.

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
- There is currently **no Neo4j/Aura CI workflow** (ephemeral graph build + smoke tests + deploy).

## Proposed approach (recommended v1)
### Unify “code CI/CD” and “graph CI/CD” under one release model
This issue should define two first-class artifact types:

1) **Application artifact** (container/package) for non-graph runtime deploys.
2) **Graph Release** (versioned, reproducible, rollbackable) for Neo4j Aura.

### Graph Release definition (what we version)
A Graph Release is an immutable bundle consisting of:
- `graph_release_id` (timestamp + git SHA)
- `pipeline_code_sha`
- `vmrs_handbook_version` + checksum
- `vendor_dataset_versions[]` + checksums
- `hitl_dataset_version` + checksum (approved set)
- `removals_version` + checksum
- a build manifest (`manifest.json`)
- build metrics (`metrics.json`) + logs
- a loadable graph snapshot artifact (format depends on Aura import path)

### HITL: local authoring + remote canonical (CI/CD evaluable)
- **Local HITL**: operators/runners produce HITL outputs locally (e.g., `HitL_local/pending/…`).
- **Remote canonical HITL**: the dataset used for beta/pilot/prod Graph Releases.

MVP guardrail:
- **Only remote-approved HITL participates in beta/pilot/prod graph builds.**
- Local HITL is promoted into the remote-approved set via a review step (PR-based or a separate approval mechanism).

### Neo4j Aura constraints that drive the design
- Aura is managed: you don’t have filesystem access to run `neo4j-admin database dump/load` on the server.
- Import/export is snapshot-based:
  - exports are `.backup` (Neo4j 5+) or `.dump` (4.x)
  - console import is limited to files <4GB
  - larger imports use `neo4j-admin database upload`
- CDC/transaction logs do **not** capture the effects of loading a dump, so lineage must be recorded outside the graph.

(See Sources at the bottom.)

## Architecture options (downtime vs zero-downtime)
### Option A: In-place overwrite (simplest, has downtime)
Use this if beta/pilot can tolerate downtime during import/restore.

```
                 +----------------------+
                 |      GitHub Actions  |
                 |  kg-build (Neo4j CI) |
                 +----------+-----------+
                            |
                            | Graph Release (snapshot artifact)
                            v
                    +---------------+
                    | Neo4j Aura    |
                    | env: beta     |
                    | (single)      |
                    +-------+-------+
                            |
                            | IMPORT/RESTORE (overwrites)
                            |  (downtime window)
                            v
                    +---------------+
                    | Neo4j Aura    |
                    | env: beta     |
                    | (updated)     |
                    +---------------+
```

Rollback (Option A): import/restore the previous snapshot into the same instance (also downtime).

### Option B: Blue/Green cutover (prod: no downtime)
Recommended for prod to avoid downtime: load the new snapshot into **green** while **blue** serves traffic, then cut over by switching the app’s Neo4j URI/secret.

```
                 +----------------------+
                 |      GitHub Actions  |
                 |  kg-build (Neo4j CI) |
                 +----------+-----------+
                            |
                            | Graph Release (snapshot artifact)
                            v
                 +-----------------------------+
                 | Neo4j Aura (env: prod)      |
                 |   BLUE: prod-blue (serving) |
                 +--------------+--------------+
                                ^
                                | bolt+s://... (current URI)
+--------------------+          |
| App / API / Agent  |----------+
| (uses Neo4j URI)   |
+----------+---------+
           |
           | cutover = switch secret/URI
           v
                 +-----------------------------+
                 | Neo4j Aura (env: prod)      |
                 |  GREEN: prod-green (new)    |
                 +--------------+--------------+
                                ^
                                |
                                | IMPORT/UPLOAD snapshot + smoke tests
                                +------------------------
```

Rollback (Option B): switch the app back to the blue URI/secret (near-instant).

Tradeoffs:
- Blue/green costs more (two Aura instances running during cutover), but gives the cleanest rollback and minimal deploy risk.
- In-place overwrite is cheaper/simpler, but makes deploys + rollbacks inherently disruptive.

## Workflow shape (GitHub Actions)
### CI (PR)
- Keep `.github/workflows/ci.yml` as-is for Python tests.
- Add `kg-data-ci.yml`:
  - validates schemas for VMRS/vendor/HITL/removals inputs
  - drift checks (counts/deltas thresholds; requires explicit approval on big swings)
  - runs an ephemeral Neo4j (Docker) and executes smoke queries

### Graph Release build (main + schedule + manual)
Add `kg-build.yml`:
- spins up ephemeral Neo4j (Docker) in CI
- loads normalized data (VMRS + vendor + remote-approved HITL + removals)
- runs validations + smoke queries
- produces:
  - `manifest.json` + `metrics.json`
  - a loadable snapshot artifact

### Deploy/promotion/rollback (manual; beta → pilot → prod)
Add:
- `kg-deploy.yml` (workflow_dispatch): deploy a selected `graph_release_id` to beta/pilot/prod
- `kg-promote.yml` (optional): promote *the same* `graph_release_id` upward
- `kg-rollback.yml`: redeploy a previous `graph_release_id`

For Aura, “deploy” should be environment-specific:
- **prod (no downtime):** blue/green cutover (import/upload into green, test, then switch URI/secret)
- **beta/pilot (decision):** either blue/green (same as prod) or in-place overwrite if downtime is acceptable

## Observability (required, not optional)
Every build/deploy run must record:
- `run_id`, `graph_release_id`, `pipeline_code_sha`
- full input lineage (dataset versions + checksums)
- build/deploy durations
- node/edge counts and deltas vs previous release
- number of removals applied
- validation + smoke-test results

Important: if snapshot load doesn’t emit CDC, then “what changed” must be inferred from (a) manifest lineage and (b) diff metrics.

## Work breakdown
E1) Repo recon (runtime + data sources)
- Identify runtime components that need deploy besides Neo4j (MCP servers? API? agents?)
- Confirm language/toolchain and existing test entrypoints (Python/Node, pytest, etc.)
- Identify where VMRS handbook/vendor/HITL/removals will live (repo vs object store)

E2) CI + data contracts
- Confirm `.github/workflows/ci.yml` is the required status check for branch protection
- Add deterministic checks you want long-term (optional: lint/format)
- Formalize canonical schemas for VMRS handbook, vendor data, HITL approved, removals
- Define drift thresholds (counts, mapping coverage, etc.) and the override process

E3) Add Neo4j-in-CI smoke tests
- run Neo4j as a GitHub Actions service container
- load a small fixture KG and run smoke Cypher queries

E4) Graph Release build pipeline
- implement a deterministic build that can recreate the graph from the manifest
- output snapshot artifact + manifest + metrics

E5) Aura deploy/rollback workflows
- define which import path we’re using (<4GB console import vs `neo4j-admin database upload`)
- implement manual deploy to beta
- implement rollback to last-known-good release

E6) Documentation
- document required secrets, environment separation, and operator runbooks

## Validation / acceptance criteria
- [ ] CI runs on PRs and blocks merge on failure
- [ ] `kg-data-ci.yml` validates graph inputs and runs Neo4j smoke tests in CI
- [ ] `kg-build.yml` produces a Graph Release artifact with manifest + metrics
- [ ] Deploy-to-beta can be executed via GH Actions for a selected `graph_release_id`
- [ ] **Prod deploy uses blue/green cutover (no downtime for the serving graph).**
- [ ] **Prod rollback is a URI/secret switch back to last-known-good (near-instant).**
- [ ] Environments + secrets separation documented

## Open questions
- Do we expect the Aura-importable snapshot to stay <4GB for MVP? (If not, standardize on `neo4j-admin database upload`.)
- For beta/pilot: can we accept deploy downtime (Option A), or should we use the same blue/green approach as prod (Option B)?
- What is the cutover mechanism for prod blue/green: app-config/secret flip, DNS, or a lightweight “Neo4j router” layer?
- Where is the remote canonical HITL dataset stored (repo vs object storage), and what is the approval workflow?

## Sources (Neo4j + GitHub Actions)
- Neo4j Operations Manual: Back up an offline database: https://neo4j.com/docs/operations-manual/current/backup-restore/offline-backup/
- Neo4j Operations Manual: Restore a database dump: https://neo4j.com/docs/operations-manual/current/backup-restore/restore-dump/
- Neo4j Operations Manual: Backup/restore planning: https://neo4j.com/docs/operations-manual/current/backup-restore/planning/
- Neo4j Aura: backup/export/restore: https://neo4j.com/docs/aura/managing-instances/backup-restore-export/
- Neo4j Operations Manual: Upload to Neo4j Aura: https://neo4j.com/docs/operations-manual/current/database-administration/standard-databases/upload-to-aura/
- GitHub Actions: Service containers: https://docs.github.com/actions/use-cases-and-examples/using-containerized-services/about-service-containers
- Neo4j Operations Manual: Docker intro/config: https://neo4j.com/docs/operations-manual/current/docker/introduction/
- Neo4j Operations Manual: Logging: https://neo4j.com/docs/operations-manual/current/monitoring/logging/
- Neo4j CDC (self-managed): https://neo4j.com/docs/cdc/current/get-started/self-managed/
