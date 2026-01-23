# HITL Step 3: richer context capture + operator metadata

## Purpose (standalone)
This plan upgrades the HITL file-first workflow so that:
- each submission carries a minimal **context pack** (enough to review without the full transcript)
- each review carries structured **operator identity** (name + role, optionally id/team)

Concretely, the goal is to **adapt the two MCP servers** (and the prompts that call them) so HITL records are shaped to **fit your existing Neo4j domain model identifiers**:
- Capture server: `mcp/hitl_get_feedback/server.py` (writes Neo4j-aligned `content.target_type` + `content.target_key`, plus `content.context_pack`)
- Review server: `mcp/hitl_review/server.py` (writes canonical `review.operator` metadata + decision fields, with back-compat)

This document is written to be **independent** of any previous HITL plans. It restates the baseline workflow, the target JSON shape, compatibility rules, and the rollout steps.

## Baseline workflow (what we are building on)
File-first HITL has two phases:
- **Capture**: agent calls `mcp_hitl.submit_knowledge(...)` → writes `HitL_local/pending/<id>.json`
- **Review**: operator calls `mcp_hitl_review.record_review(...)` → writes reviewed JSON in:
  - `HitL_local/reviewed/approved/<id>.json` or
  - `HitL_local/reviewed/rejected/<id>.json`

If your repo currently only has capture (no review), you can still implement the capture-side schema additions in this plan first; review-side additions apply once review tooling exists.

## End user context
- **Primary user (operator)**: fleet team operator (non-technical) reviewing HITL submissions; needs quick, trustworthy context to decide approve/reject and leave short notes.
- **Secondary user (engineer/analyst)**: maintains prompts + ingestion pipeline; needs submissions to be structured enough to incorporate later (files now → Neo4j nodes later).
- **Submitter (Claude Desktop user)**: asks questions / provides feedback; expects feedback is recorded without friction; may share sensitive info unintentionally.

## User requirements
- **Actionable context**: every submission should include enough “why + what + evidence” that an operator can decide without needing full chat transcript.
- **Reproducibility**: capture the exact user question that triggered the submission, and a short excerpt of the assistant answer (or summary) so the issue can be reproduced.
- **Operator identity**: review records should store the operator’s **name** and **role** (and optionally an operator id), so audits and accountability are possible.
- **Submitter identity**: submissions should store the submitter’s **name** and **role** (and optionally an id/team), so you can follow up and audit who proposed changes.
- **Privacy-safe by default**: avoid storing full transcripts or unnecessary PII; store only minimal excerpts and structured fields.
- **Backwards compatible**: existing files like `HitL_local/reviewed/approved/*.json` should remain readable; new fields should be additive.

## Architecture diagrams

### High-level (C4 Level 1: System Context)
```
Person: Claude Desktop user
  |
  v
System: VMRS Chatbot + HITL (this repo)
  - captures HITL submissions for later review
  - supports operator review/approval (file-first)
  |
  +--> External: Local filesystem (HitL_local/*)
  |
  +--> Person: Fleet operator (reviews/approves/rejects submissions)
```

### Low-level (C4 Level 2: Containers + data stores)
```
Container: Lookup agent (Claude Desktop prompt-driven)
  - uses: interface prompts/lookup_agent/hitl_feedback_capture.txt
  - calls: mcp_hitl.submit_knowledge(...)
        |
        v
Container: HITL capture MCP server (Python)
- impl: mcp/hitl_get_feedback/server.py
  - responsibility: validate + persist pending submissions
        |
        v
Data store (local): HitL_local/pending/<submission_id>.json
        |
        v
Container: HITL review agent (operator-facing)
  - uses: interface prompts/hitl_review_agent/main_v1.txt
  - calls: mcp_hitl_review.record_review(...)
        |
        v
Container: HITL review MCP server (Python)
  - impl: mcp/hitl_review/server.py
  - responsibility: move file + persist review metadata + decision
        |
        +--> Data store (local): HitL_local/reviewed/approved/<submission_id>.json
        |
        +--> Data store (local): HitL_local/reviewed/rejected/<submission_id>.json
```

### Low-level (arc42 Runtime View: core scenarios)
#### Scenario A: capture a submission (file-first)
```
User asks question / provides feedback
  -> Lookup agent decides “save via HITL”
  -> mcp_hitl.submit_knowledge(...)
  -> write local JSON: HitL_local/pending/<id>.json
  -> return <id> to chat
```

#### Scenario B: review a submission (operator decision)
```
Operator lists pending submissions
  -> mcp_hitl_review.list_submissions(location="pending")
Operator opens a submission
  -> mcp_hitl_review.get_submission(<id>)
Operator approves/rejects (with notes + operator identity)
  -> mcp_hitl_review.record_review(...)
  -> move pending file + write reviewed JSON:
       - approved: HitL_local/reviewed/approved/<id>.json
       - rejected: HitL_local/reviewed/rejected/<id>.json
```

## Goals
- **Standardize a minimal “context pack”** that makes submissions independently reviewable.
- **Capture structured operator metadata** on review (name, role; optional id/team).
- **Preserve long-term compatibility** with `HitL_local/hitl_design.md` (provenance: who/what/when/why).

## Neo4j alignment (supplement the current data model)
HITL is a **workflow + provenance layer** that supplements (not replaces) the existing Neo4j domain graph:
- Domain labels: `System`, `Assembly`, `Component`, `Vendor`, `VendorPart`
- Domain identifier conventions (already in your schema):
  - `System.code`, `Assembly.code`, `Component.code` (indexed)
  - `Vendor.code` (indexed)
  - `VendorPart.part` (indexed)
- Domain timestamps use integers like `updated_at: INTEGER`. HITL already uses epoch millis integers (`*_at_ms`) and should keep doing so.

### Canonical target conventions (so HITL can attach to domain nodes later)
When a submission refers to an existing Neo4j node, use:
- `content.target_type`: one of `System|Assembly|Component|Vendor|VendorPart`
- `content.target_key`: minimal stable key matching the domain schema:
  - for `System|Assembly|Component|Vendor`: `{"code": "<code>"}`
  - for `VendorPart`: `{"part": "<part>"}`

### Multiple targets (common in real submissions)
Some submissions are relevant to **multiple** domain nodes (e.g., multiple `VendorPart`s mapping to a `Component`, or multiple candidate `Component` codes).

Additive extension:
- `content.targets`: list of Neo4j-aligned targets:
  - each item includes `target_type` and `target_key` (same conventions as above)
Invariants (to avoid ambiguity):
- If `content.targets` is present, it must be a **non-empty list**.
- If `content.targets` is present, then `content.target_type` and `content.target_key` must **mirror** `content.targets[0].target_type` and `content.targets[0].target_key`.

Compatibility rule:
- Keep `content.target_type` + `content.target_key` as the **primary** target for legacy readers.
- When `content.targets` is present, treat `content.targets[0]` as the canonical primary target and mirror it into `content.target_type`/`content.target_key`.

Optional convenience fields (allowed, but not required):
- `content.vmrs_code`: if present, it should match `Component.code`
- `content.vendor_code`: if present, it should match `Vendor.code`
- `content.vendor_part_part`: if present, it should match `VendorPart.part`

### Example “about” mapping (future Neo4j ingestion, not required for file MVP)
If/when HITL is ingested into Neo4j as separate nodes (e.g. `:HitlSubmission`), the intended linkage is:
- `(:HitlSubmission)-[:ABOUT]->(:Component {code})` when `target_type="Component"` or `vmrs_code` is provided
- `(:HitlSubmission)-[:ABOUT]->(:VendorPart {part})` when `target_type="VendorPart"`
- `(:HitlSubmission)-[:ABOUT]->(:Vendor {code})` when `target_type="Vendor"`

This keeps HITL records queryable alongside the domain model (e.g., “show all pending submissions about Component 047-000-000”) without forcing HITL to share the exact same properties as domain nodes.

## Non-goals
- **Full transcript capture** (Claude Desktop limitation + privacy risk).
- **Authentication/authorization** for operators (still local/dev).
- **Automatic incorporation into Neo4j** (separate step after review stabilizes).
- **UI** beyond the existing agent-driven workflow.

## Success metrics
- **Context completeness**: ≥ 80% of new submissions include `content.context_pack.related_query` and `content.context_pack.answer_excerpt_or_summary`.
- **Operator completeness**: ≥ 95% of reviews include `review.operator.name` and `review.operator.role`.
- **Review efficiency**: median operator time-to-decision decreases (baseline now vs after context pack rollout).
- **Zero breakage**: `mcp/hitl_review/server.py` can still summarize/read older reviewed JSON without errors.

## Proposed data model changes (minimal, additive)

### 1) Add a submission `schema_version`
Add at top-level:
- `schema_version`: integer (start at `2` for “context_pack + review.operator”)
Defaulting rule:
- If `schema_version` is missing, treat it as `1` (legacy shape).

### 2) Add a structured `content.context_pack` (keep existing `content.context`)
Keep existing fields (`description`, `context`, `related_query`, etc.) and add:
```json
"content": {
  "description": "...",
  "context": "... (optional free text)",
  "related_query": "...",
  "context_pack": {
    "related_query": "exact user question (duplicate ok for convenience)",
    "answer_excerpt_or_summary": "short excerpt/summary of assistant answer (<= ~500 chars)",
    "why_saved": "1–2 sentences: why this needs operator attention",
    "evidence": [
      {"type": "user_claim|url|quote|file|screenshot_ref", "value": "..."}
    ],
    "expected_vs_observed": {
      "expected": "what should be true",
      "observed": "what the assistant/graph currently implies"
    }
  }
}
```
Notes:
- This is intentionally small; it’s the minimum to make `description` self-contained and reviewable.
- `evidence` stays flexible (typed list) without forcing heavy schema work.
- `screenshot_ref` must be a **text-only reference** (e.g. “see ticket ABC-123”, “see Slack message timestamp …”); do not store binary images in the JSON.
- Length rule: `context_pack.answer_excerpt_or_summary` should be **≤ 500 characters**; if longer, the capture MCP should return an error telling the caller to shorten it (do not silently store large excerpts).

### Precedence rules (avoid drift while “write both”)
During the transition, the same concept may exist in two places. To avoid divergence:
- **Targets**
  - **Write**: if `content.targets` is present, mirror `content.targets[0]` into `content.target_type`/`content.target_key`.
  - **Read**: prefer `content.targets` when present; otherwise fall back to `content.target_type`/`content.target_key`.
- **Query that triggered the submission**
  - **Write**: write both `content.related_query` and `content.context_pack.related_query` when possible.
  - **Read**: prefer `content.context_pack.related_query`, fallback to `content.related_query`.
- **Review decision metadata**
  - **Write**: always write `review.*` (canonical) and mirror legacy top-level fields derived from it.
  - **Read**: prefer `review.*`, fallback to legacy top-level fields.

### `status` lifecycle (avoid ambiguity)
- Pending submission file: `status = "pending"`
- Reviewed submission file: set `status = "reviewed"` and rely on `review.decision` for `approved|rejected`
  - (Alternative is `status = "approved|rejected"`, but this plan uses `"reviewed"` to keep “status” distinct from “decision”.)

### 3) Replace top-level review fields with a nested `review` object (while keeping backward compatibility)

Target shape for new/updated reviewed submissions:
```json
"review": {
  "decision": "approved|rejected",
  "reviewed_at_ms": 1737469000000,
  "notes": "Why this was approved/rejected (1–3 sentences)",
  "operator": {
    "id": "op-123 (optional but recommended)",
    "name": "Jane Operator (required)",
    "role": "Fleet Analyst (required)",
    "team": "Fleet Ops (optional)"
  }
}
```

Compatibility strategy (minimal risk):
- **Write both** (for now): keep current top-level fields (`decision`, `reviewed_at_ms`, `reviewed_by`, `review_notes`) but treat `review.*` as canonical going forward.
- **Read both**: update any summarizers/read paths to prefer `review.*` when present, else fall back to the existing top-level fields.

## MCP API changes (minimal)

### Capture server: `mcp/hitl_get_feedback/server.py`
Add optional parameters to `submit_knowledge` (additive, does not break callers):
- `context_pack: Optional[Dict[str, Any]] = None`
- `targets: Optional[List[Dict[str, Any]]] = None`
- `submitter: Optional[Dict[str, Any]] = None`

Write them into the submission JSON (additive):
- `schema_version = 2`
- `content.context_pack = context_pack` (if provided)
- `content.targets = targets` (if provided)
  - if `content.targets` is present, also mirror `targets[0]` into `content.target_type` and `content.target_key` for backward compatibility
- `submitter = submitter` (if provided; keep minimal and privacy-safe)

Recommended privacy-safe `submitter` shape (name + role captured):
```json
"submitter": {
  "id": "user-123 (optional)",
  "name": "Alex Submitter (recommended)",
  "role": "Fleet Ops (recommended)",
  "team": "Fleet Ops (optional)",
  "channel": "claude_desktop",
  "label": "optional free-text (e.g., 'claude_desktop_user')"
}
```

Validation rule (MVP-appropriate):
- If `submitter.name` is provided, also require `submitter.role` (and vice versa). Otherwise allow the minimal `{channel,label}` form to avoid breaking older callers.
- If `context_pack.answer_excerpt_or_summary` is provided and exceeds 500 characters, return an error advising the caller to shorten the excerpt to ≤ 500 characters.

### Review server: `mcp/hitl_review/server.py`
Evolve `record_review` with additive optional parameters:
- `operator_name: Optional[str] = None`
- `operator_role: Optional[str] = None`
- `operator_id: Optional[str] = None`
- `operator_team: Optional[str] = None`

Persist review using the nested object (and also write existing fields for back-compat):
- `review = { decision, reviewed_at_ms, notes, operator: {...} }`
- `decision` (top-level) = `review.decision`
- `reviewed_at_ms` (top-level) = `review.reviewed_at_ms`
- `review_notes` (top-level) = `review.notes`
- `reviewed_by` (top-level) = `operator_id or operator_name or reviewed_by`

Validation rules (MVP-appropriate):
- Keep `review_notes` required (as today).
- Require **operator_name + operator_role** if provided at all; otherwise allow legacy `reviewed_by` only (to avoid breaking existing operator workflows).

## Disk JSON schemas (before → after)
These examples show the concrete **data shape written to disk** by each MCP server.

### Capture server (`mcp/hitl_get_feedback/server.py`) output (pending submission)
File path: `HitL_local/pending/<id>.json`

Before (baseline pending submission):
```json
{
  "id": "HITL-<id>",
  "type": "correction|addition|context|question",
  "submitted_at_ms": 1737465030000,
  "status": "pending",
  "content": {
    "description": "What the user wants to record",
    "context": "Why this is valuable (optional)",
    "related_query": "Query that prompted this (optional)",
    "target_type": "Component",
    "target_key": { "code": "047-000-000" },
    "proposed_action": "set_property|add_relationship|remove_relationship",
    "proposed_payload": { "name": "New official name" }
  }
}
```

After (schema v2: Neo4j-aligned target + context pack):
```json
{
  "schema_version": 2,
  "id": "HITL-<id>",
  "type": "correction|addition|context|question",
  "submitted_at_ms": 1737465030000,
  "status": "pending",
  "submitter": {
    "id": "user-123",
    "name": "Alex Submitter",
    "role": "Fleet Ops",
    "team": "Fleet Ops",
    "channel": "claude_desktop",
    "label": "claude_desktop_user"
  },
  "content": {
    "description": "What the user wants to record",
    "context": "Why this is valuable (optional)",
    "related_query": "Query that prompted this (optional)",
    "target_type": "Component",
    "target_key": { "code": "047-000-000" },
    "targets": [
      { "target_type": "Component", "target_key": { "code": "047-000-000" } },
      { "target_type": "VendorPart", "target_key": { "part": "ABC-123" } }
    ],
    "proposed_action": "set_property|add_relationship|remove_relationship",
    "proposed_payload": { "name": "New official name" },
    "context_pack": {
      "related_query": "Exact user question (duplicate ok)",
      "answer_excerpt_or_summary": "Short excerpt/summary of assistant answer",
      "why_saved": "Why this needs operator attention",
      "evidence": [{ "type": "user_claim", "value": "User says ..." }],
      "expected_vs_observed": { "expected": "What should be true", "observed": "What was observed" }
    }
  }
}
```

### Review server (`mcp/hitl_review/server.py`) output (reviewed submission)
File path: `HitL_local/reviewed/approved/<id>.json` or `HitL_local/reviewed/rejected/<id>.json`

Before (baseline reviewed submission; legacy top-level review fields only):
```json
{
  "id": "HITL-<id>",
  "type": "correction|addition|context|question",
  "submitted_at_ms": 1737465030000,
  "status": "reviewed",
  "content": {
    "description": "What the user wants to record",
    "target_type": "VendorPart",
    "target_key": { "part": "ABC-123" },
    "proposed_action": "set_property",
    "proposed_payload": { "vmrs": "047-000-000" }
  },
  "reviewed_at_ms": 1737469000000,
  "decision": "approved",
  "review_notes": "Why this was approved/rejected",
  "reviewed_by": "Jane Operator"
}
```
Note: if you already have legacy reviewed files with `status: "pending"`, treat `decision`/`reviewed_at_ms` (and the reviewed folder path) as authoritative; `status` should be considered advisory during the transition.

After (schema v2: canonical `review` object + mirrored legacy fields):
```json
{
  "schema_version": 2,
  "id": "HITL-<id>",
  "type": "correction|addition|context|question",
  "submitted_at_ms": 1737465030000,
  "status": "reviewed",
  "content": {
    "description": "What the user wants to record",
    "target_type": "VendorPart",
    "target_key": { "part": "ABC-123" },
    "targets": [
      { "target_type": "VendorPart", "target_key": { "part": "ABC-123" } },
      { "target_type": "Component", "target_key": { "code": "047-000-000" } },
      ...
    ],
    "proposed_action": "set_property",
    "proposed_payload": { "vmrs": "047-000-000" },
    "context_pack": {
      "related_query": "Exact user question (duplicate ok)",
      "answer_excerpt_or_summary": "Short excerpt/summary of assistant answer",
      "why_saved": "Why this needs operator attention",
      "evidence": [{ "type": "user_claim", "value": "User says ..." }],
      "expected_vs_observed": { "expected": "What should be true", "observed": "What was observed" }
    }
  },
  "review": {
    "decision": "approved",
    "reviewed_at_ms": 1737469000000,
    "notes": "Why this was approved/rejected",
    "operator": {
      "id": "op-123",
      "name": "Jane Operator",
      "role": "Fleet Analyst",
      "team": "Fleet Ops"
    }
  },
  "reviewed_at_ms": 1737469000000,
  "decision": "approved",
  "review_notes": "Why this was approved/rejected",
  "reviewed_by": "op-123"
}
```

## Prompt changes (so the agent actually supplies the new fields)

### Capture prompt: `interface prompts/lookup_agent/hitl_feedback_capture.txt`
Update guidance so the lookup agent captures a `context_pack` with:
- `answer_excerpt_or_summary` (short)
- `why_saved` (explicit)
- `expected_vs_observed` (if it’s a correction)
- `evidence` items (even if just `{"type":"user_claim","value":"..."}`)

Also update the “MVP scope” line if it incorrectly claims review/approval is unsupported for your current setup.

### Review agent prompt: `interface prompts/hitl_review_agent/main_v1.txt`
At session start (once), collect operator identity:
- **Name** (required)
- **Role** (required)
- Optional: team + operator id

Then pass those fields into `record_review(...)` on every approval/rejection.

## Rollout plan (small, safe steps)
- **Step A (capture schema + writing)**: implement the new optional fields and start writing `schema_version=2` and `content.context_pack` on new submissions.
- **Step B (review schema + writing)**: implement `review.operator` (and mirrored legacy fields) when reviews are recorded.
- **Step C (read compatibility)**: update any readers/summarizers to follow the precedence rules and never fail on older JSON.
- **Step D (prompt adoption)**: update both prompts so the new fields are routinely populated.
- **Step E (metrics check)**: spot-check the next ~20 submissions and ~20 reviews to confirm context/operator completeness targets.

## Risks and mitigations
- **PII creep** (operators paste too much): mitigate by explicitly instructing “no full transcript; excerpt only; redact sensitive identifiers.”
- **Schema drift** (free-form dicts get messy): mitigate by adding `schema_version` + keeping the context pack minimal.
- **Back-compat bugs**: mitigate by preferring additive changes and “read both / write both” during transition.

## Best-practice references (required)
- Provenance concepts (Entity/Activity/Agent/time): `https://www.w3.org/TR/prov-dm/`
- Neo4j workflow/state modeling inspiration: `https://neo4j.com/blog/part-1-using-neo4j-in-business-process-modeling-scenarios/`
- Neo4j temporal values (useful for time handling/rendering): `https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/`
- Log content guidance (avoid sensitive data, keep logs useful): `https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html`
- Log management background (auditability, retention concepts): `https://csrc.nist.gov/publications/detail/sp/800-92/final`
