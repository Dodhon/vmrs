# HITL Step 3: richer context capture + operator metadata

## End user context
- **Primary user (operator)**: fleet team operator (non-technical) reviewing HITL submissions; needs quick, trustworthy context to decide approve/reject and leave short notes.
- **Secondary user (engineer/analyst)**: maintains prompts + ingestion pipeline; needs submissions to be structured enough to incorporate later (files now → Neo4j nodes later).
- **Submitter (Claude Desktop user)**: asks questions / provides feedback; expects feedback is recorded without friction; may share sensitive info unintentionally.

## User requirements
- **Actionable context**: every submission should include enough “why + what + evidence” that an operator can decide without needing full chat transcript.
- **Reproducibility**: capture the exact user question that triggered the submission, and a short excerpt of the assistant answer (or summary) so the issue can be reproduced.
- **Operator identity**: review records should store the operator’s **name** and **role** (and optionally an operator id), so audits and accountability are possible.
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
  - impl: mcp/hitl/server.py
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

### Capture server: `mcp/hitl/server.py`
Add optional parameters to `submit_knowledge` (additive, does not break callers):
- `context_pack: Optional[Dict[str, Any]] = None`
- `submitter: Optional[Dict[str, Any]] = None`

Write them into the submission JSON (additive):
- `schema_version = 2`
- `content.context_pack = context_pack` (if provided)
- `submitter = submitter` (if provided; keep minimal and privacy-safe)

Recommended minimal `submitter` shape:
```json
"submitter": {
  "label": "optional free-text (e.g., 'claude_desktop_user')",
  "channel": "claude_desktop"
}
```

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

## Prompt changes (so the agent actually supplies the new fields)

### Capture prompt: `interface prompts/lookup_agent/hitl_feedback_capture.txt`
Update guidance so the lookup agent captures a `context_pack` with:
- `answer_excerpt_or_summary` (short)
- `why_saved` (explicit)
- `expected_vs_observed` (if it’s a correction)
- `evidence` items (even if just `{"type":"user_claim","value":"..."}`)

Also update the “MVP scope” line (it currently says “does not support review/approval actions yet”) since Step 2 exists.

### Review agent prompt: `interface prompts/hitl_review_agent/main_v1.txt`
At session start (once), collect operator identity:
- **Name** (required)
- **Role** (required)
- Optional: team + operator id

Then pass those fields into `record_review(...)` on every approval/rejection.

## Rollout plan (small, safe steps)
- **Step A (schema + writing)**: implement the new optional fields and start writing `schema_version=2`, `content.context_pack`, and `review.operator`.
- **Step B (read compatibility)**: update review summarization to surface operator name/role when present, but never fail on older JSON.
- **Step C (prompt adoption)**: update both prompts so the new fields are routinely populated.
- **Step D (metrics check)**: spot-check the next ~20 submissions to confirm context/operator completeness targets.

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
