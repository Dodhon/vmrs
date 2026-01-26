## Backlog Project automation upgrades (Issue #18)

### Tracking links (ad hoc)
- **Issue**: `https://github.com/Dodhon/vmrs/issues/18`
- **PR**: (add when opened) `https://github.com/Dodhon/vmrs/pull/<TBD>`

### End user context
- **Who**: Repo owner/operator (you) who triages work in the GitHub Project `Backlog` and uses an AI coding agent that follows repo workflows.
- **Goal**: When you open/reopen an issue or PR, it should automatically appear in the `Backlog` project with sensible default fields, so you don’t do repetitive manual triage.

### User requirements
- **Auto-add**: New/reopened **issues and PRs** get added to `https://github.com/users/Dodhon/projects/1`.
- **Auto-triage**: Project fields are auto-set (minimum: `Status=Todo`; plus best-effort `Area`, `Priority`/`Importance` based on labels).
- **Default assignment**: On issue opened/reopened, assign to `Dodhon` if unassigned.
- **Lifecycle**: When an issue/PR is **completed** (closed), the Project item is updated to `Status=Done`.
- **Backfill**: Provide a one-time (manual) backfill automation to add existing open issues/PRs to the Project and set baseline fields.
- **Agent guidance**: Update `.claude/skills/github-cli-workflow/SKILL.md` so future agents follow the updated best practices + troubleshooting.

### Architecture diagram
#### C4 Level 1 (System Context)
```
Person (Repo owner/operator)
  |
  | creates/updates Issues & PRs
  v
GitHub Repo (Dodhon/vmrs) ------------------------------+
  |                                                    |
  | triggers events                                    | stores project items + fields
  v                                                    v
GitHub Actions workflow (.github/workflows/add-to-project.yml) ---> GitHub ProjectV2 "Backlog"
  |
  | uses PAT from repo secrets for Projects API access
  v
GitHub API (GraphQL ProjectV2 + REST/GraphQL for assignees)
```

#### C4 Level 2 (Containers + data stores)
```
Container: GitHub Actions Job (ubuntu-latest)
  - reads event payload (issue/pr node_id, labels, assignees, closed state)
  - calls GitHub GraphQL:
      - addProjectV2ItemById (create project item)
      - updateProjectV2ItemFieldValue (set Status/Area/Priority/etc)
      - query project fields/options (resolve IDs by name)
  - calls GitHub REST/GraphQL (issues only):
      - assign default owner (if unassigned)

Data stores (external):
  - GitHub ProjectV2 "Backlog" (items + field values)
  - GitHub Repo metadata (issues/PRs, labels, assignees)

Secrets/config:
  - Repo secret: ADD_TO_PROJECT_PAT (fine-grained/classic token)
```

#### Existing flow diagram (high-level)
```
Issue/PR opened or reopened
        |
        v
GitHub Actions workflow (.github/workflows/add-to-project.yml)
  - (issues) assign default owner (if none)
  - add issue/PR to ProjectV2 (Backlog)
  - set ProjectV2 fields (Status/Area/Priority/Importance)
        |
        v
GitHub Project "Backlog" reflects consistent triage metadata
```

### Runtime view (arc42)
#### Scenario A: Issue opened/reopened
1. GitHub emits `issues.opened` or `issues.reopened`.
2. Workflow computes `CONTENT_ID` from `github.event.issue.node_id`.
3. Workflow ensures a Project item exists for this content (idempotent add).
4. If no assignees, workflow assigns `Dodhon`.
5. Workflow sets Project `Status=Todo`, then best-effort sets `Area`/`Priority` based on labels.

#### Scenario B: PR opened/reopened
1. GitHub emits `pull_request.opened` or `pull_request.reopened`.
2. Workflow computes `CONTENT_ID` from `github.event.pull_request.node_id`.
3. Workflow ensures a Project item exists for this content (idempotent add).
4. Workflow sets Project `Status=Todo`, then best-effort sets `Area`/`Priority` based on labels.

#### Scenario C: Issue/PR closed
1. GitHub emits `issues.closed` or `pull_request.closed` (merged PRs are also `closed`).
2. Workflow ensures a Project item exists for this content (idempotent add).
3. Workflow sets Project `Status=Done`.

#### Scenario D: Manual backfill
1. Operator runs `workflow_dispatch`.
2. Workflow enumerates all open issues and open PRs.
3. For each, ensure Project item exists (idempotent add) and set baseline `Status=Todo`.

### Goals
- Expand existing workflow in `.github/workflows/add-to-project.yml` to include PR events.
- Set ProjectV2 fields deterministically and safely (no hard failures if labels are missing/unmapped).
- Ensure closed items are consistently reflected as `Status=Done` in the Project.
- Provide a simple backfill mechanism to avoid “reopen to add” hacks.
- Keep implementation minimal, repo-local, and easy to modify as the project fields evolve.
- Document conventions (labels → fields mapping) in a single place.

### Non-goals (explicitly out of scope for v1)
- Eliminating PAT usage entirely (token hardening is tracked as follow-up).
- Auto-archiving closed items (we can add later once we agree on timing/policy).

### Success metrics
- **Correctness**: A newly opened issue and a newly opened PR both appear in `Backlog` within ~1 minute.
- **Field coverage**:
  - `Status` is set to `Todo` for both issue and PR items.
  - `Area` and `Priority`/`Importance` are set when a mapping label exists; otherwise left unchanged (or set to a safe default, if we decide to).
- **Lifecycle correctness**: When an issue/PR is closed, the Project item `Status` becomes `Done` within ~1 minute.
- **Backfill correctness**: A manual backfill run adds all currently-open issues/PRs to the Project (idempotent) and sets at least `Status=Todo`.
- **Resilience**: Workflow run succeeds even if:
  - labels are absent
  - mapping labels are unknown
  - item is already in the project (idempotent add)

### Label → Project field mapping contract (v1)
- **Supported label formats (minimal)**:
  - `area:<AREA_OPTION>` → sets Project single-select field `Area` to `<AREA_OPTION>`
  - `priority:P0` / `priority:P1` / `priority:P2` → sets Project single-select field `Priority`
- **Fallback behavior**:
  - If no mapping label exists (or unknown value), only set `Status` and skip other fields (no failures).
- **Notes**:
  - If your project uses `Importance` instead of `Priority`, treat this as “one or the other” for v1: choose the actual single-select field that exists and map labels to that field only.

### Implementation plan (minimal-first)
1. **Update workflow triggers**
   - Add `pull_request` triggers: `opened`, `reopened` (optionally `ready_for_review` later).
   - Add lifecycle triggers:
     - `issues`: `closed`
     - `pull_request`: `closed`
   - Add `workflow_dispatch` for backfill (manual run).
2. **Unify “content ID” extraction**
   - For issues: use `github.event.issue.node_id`.
   - For PRs: use `github.event.pull_request.node_id`.
   - Store as `CONTENT_ID` env var so the rest of the workflow is shared.
3. **Add/keep “add to project” step**
   - Either:
     - Keep `actions/add-to-project@v1.0.2` for simple adds; then separately discover the Project item id, or
     - (Preferred for field setting) Use GraphQL `addProjectV2ItemById` directly so we always capture `ITEM_ID`.
   - **Idempotency requirement**:
     - **Do not scan/paginate the whole Project** to find an existing item (gets brittle as the project grows).
     - Instead, query the **Issue/PR node** for its existing Project items and check whether it already has an item for the target Project (`Backlog`).
     - If it exists, reuse that `ITEM_ID` and skip add.
     - If it doesn’t exist, call `addProjectV2ItemById` and capture the returned `ITEM_ID`.
     - This keeps idempotency fast and deterministic because you’re asking “is this content already in this project?” rather than “does this project contain this content somewhere?”
4. **Fetch Project field/option IDs**
   - Query ProjectV2 fields once per run (GraphQL) and parse:
     - `Status` field ID + `Todo` option ID
     - `Area` field ID + option IDs
     - `Priority` field ID + option IDs (P0/P1/P2)
     - `Importance` field: decide whether it’s actually a field we can set via API (if it’s a text/number field, set it; if it’s derived/unsupported, skip).
   - **Field resolution behavior (explicit)**
     - `Status` is the only required field for v1:
       - If the `Status` field is not found (by name), or `Todo`/`Done` options are missing, **fail the workflow** with a clear error message (so we don’t silently “succeed” while doing nothing).
     - `Area` and `Priority`/`Importance` are best-effort:
       - If the field is missing or the option value can’t be resolved, **skip setting it** and keep the run green.
5. **Compute desired field values from labels**
   - Minimal mapping rule:
     - If label exists like `area:<x>` or `Area`-style labels exist, map → `Area` single-select.
     - If label exists like `P0`/`P1`/`P2` (or `priority:P0`), map → `Priority` single-select.
     - Otherwise: only set `Status=Todo`.
   - Keep mappings in one place:
     - inline in the workflow as a small bash case statement, or
     - a small repo script under `scripts/` (only if needed).
   - **Event payload handling (explicit)**
     - Labels live in different places depending on event type; normalize early into one variable:
       - Issues events: `github.event.issue.labels`
       - PR events: `github.event.pull_request.labels`
     - Closed events should still set `Status=Done` regardless of labels (labels are optional input, not required state).
6. **Set ProjectV2 fields**
   - Use `updateProjectV2ItemFieldValue` (single-select values).
   - Ensure this step never fails the workflow due to missing mapping (guard checks).
7. **Default assignee**
   - On `issues` events only: if issue has no assignees, assign `Dodhon`.
   - Implement via REST API (or GraphQL `addAssigneesToAssignable`) using the same token used for project operations.
8. **Lifecycle updates**
   - On `issues.closed` and `pull_request.closed`:
     - Ensure the item exists in the Project (add if missing).
     - Set `Status=Done`.
   - Interpretation of “completed”: we use the GitHub closed state as the source of truth.
9. **Backfill automation**
   - Add `workflow_dispatch` input(s) (minimal: none; optional: `dry_run`).
   - Enumerate open issues + open PRs in this repo and add each to Project (idempotent), setting baseline fields (at least `Status=Todo`).
   - **Pagination requirement (explicit)**:
     - Use GraphQL to list repository issues/PRs with `states: OPEN` and page via `pageInfo { hasNextPage endCursor }`.
     - Loop until `hasNextPage=false` (do not assume a small number of open items).
10. **Update agent-facing workflow docs**
   - Update `.claude/skills/github-cli-workflow/SKILL.md` to reflect:
     - PRs are also auto-added
     - label conventions that drive project field setting
     - common failure modes (PAT scopes/rotation; “resource not accessible”)
11. **Verification**
   - Open a throwaway issue + PR; confirm:
     - both are added to Project
     - `Status=Todo`
     - mapping works for at least one label in each category (Area/Priority)
   - Close the issue + close/merge the PR; confirm:
     - Project `Status=Done`
   - Run the manual backfill; confirm:
     - it completes successfully and is idempotent
   - Check workflow runs with `gh run list` / `gh run view --log`.

### Testing plan (minimal, end-to-end)
- **Pre-reqs**
  - Confirm repo secret `ADD_TO_PROJECT_PAT` exists and has:
    - Projects (v2) access for the target user project
    - Permission to assign issues in `Dodhon/vmrs` (for default assignee behavior)
  - Confirm the `Backlog` project contains:
    - single-select field `Status` with options `Todo` and `Done` (required)
    - optional single-select field `Area`
    - optional single-select field `Priority` or `Importance`

- **Test 1: Issue opened → added + Status=Todo + default assignee**
  - Create a new issue with no assignees.
  - Expected within ~1 minute:
    - Project item exists in `Backlog`
    - Project `Status=Todo`
    - Issue is assigned to `Dodhon`
  - Add mapping labels (e.g. `area:<some-option>`, `priority:P1`), then reopen a new issue or retrigger with a fresh issue (v1 does not require “on label change” behavior).

- **Test 2: PR opened → added + Status=Todo**
  - Open a PR.
  - Expected within ~1 minute:
    - Project item exists in `Backlog`
    - Project `Status=Todo`
  - If PR has mapping labels, verify `Area`/`Priority` set when resolvable.

- **Test 3: Close lifecycle → Status=Done**
  - Close the test issue.
  - Close or merge the test PR.
  - Expected within ~1 minute:
    - Both project items have `Status=Done`

- **Test 4: Idempotency**
  - Reopen the same issue and PR.
  - Expected:
    - No duplicate project items created (same content maps to a single project item)
    - `Status` returns to `Todo` on reopen

- **Test 5: Backfill**
  - Create at least 2 open issues and 2 open PRs (or use existing ones).
  - Run the backfill via `workflow_dispatch`.
  - Expected:
    - All open issues/PRs are present in the project
    - Baseline `Status=Todo` set
    - Rerunning backfill is safe (no duplicates; no hard failures)

- **Failure-mode checks (fast)**
  - Temporarily remove/rename a mapping label or use an unknown mapping value.
  - Expected:
    - Workflow still succeeds; only `Status` is set.
  - If `Status`/`Todo`/`Done` is missing in the project schema:
    - Expected: workflow fails with a clear error indicating the missing field/option.

### Risks / pitfalls
- **Token scope**: Project automation requires PAT/App token; `GITHUB_TOKEN` can’t access Projects (`Automating Projects using Actions` docs).
- **Field/API limitations**: Not all “fields” are settable via `updateProjectV2ItemFieldValue` (assignees/labels are properties of the Issue/PR, not the Project item).
- **Schema drift**: If Project field names/options change, parsing by name must be updated.

### References (best-practice docs)
- GitHub Docs: Automating Projects using Actions: `https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions`
- GitHub Docs: Using the API to manage Projects (ProjectV2 GraphQL, add + update field value): `https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects`
- GitHub Docs: REST API endpoints for issue assignees (assign default owner): `https://docs.github.com/en/rest/issues/assignees`
