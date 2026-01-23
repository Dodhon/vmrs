# HITL Design Notes (Long-term + MVP)

## What HITL is doing (first principles)

A human-in-the-loop (HITL) system for a knowledge graph has two different responsibilities:

- **Capture proposals about the world** (messy, conflicting, incomplete, sometimes wrong).
- **Maintain a current working graph state** (useful defaults for queries, but revisable).

Long-term, this pushes you toward **two layers**:

1. **Proposal / review layer** (auditable; ideally append-only-ish)
2. **Published KG layer** (the current `System/Assembly/Component/Vendor/VendorPart` graph users query)

This is consistent with provenance thinking: provenance records **entities, activities, agents, and time** so users can judge trustworthiness and responsibility. (Source: [W3C PROV-DM](https://www.w3.org/TR/prov-dm/))


## Long-term Neo4j model (recommended)

### 1) Store HITL as first-class nodes

Create a node like:

- `(:HitlSubmission { id, type, status, description, context?, related_query?, submitted_at_ms, ... })`

Rationale: review is a workflow (pending → reviewed/approved/rejected). Neo4j’s workflow/state modeling example uses Requests, States, and lifecycle metadata to answer operational questions (“what’s pending”, “who approved”, “what notes”). (Source: [Neo4j BPM modeling example](https://neo4j.com/blog/part-1-using-neo4j-in-business-process-modeling-scenarios/))


### 2) Store the *proposed change intent* explicitly

If HITL will eventually be incorporated, you want more than plain text. Suggested minimal intent structure:

- `proposed_action`: `"set_property" | "add_relationship" | "remove_relationship" | "merge_nodes" | ...`
- `target_type`: label/type to be changed (e.g. `"Component"`, `"VendorPart"`)
- `target_key`: stable identifier (e.g. `{code: "047-000-000"}` or `{part: "..."}`)
- `proposed_payload`: the change details (property/value, relationship endpoints, etc.)

This avoids “free text only” submissions that are hard to apply consistently later.


### 3) Link submissions to affected domain nodes when possible

Use relationships like:

- `(:HitlSubmission)-[:ABOUT]->(:Component)` when VMRS code resolves
- optionally `(:HitlSubmission)-[:ABOUT]->(:VendorPart)` for vendor-part-specific feedback

This makes human review faster (reviewer clicks/queries around the impacted area).


### 4) Review decisions: properties (simple) vs events (audit-grade)

Two legitimate patterns:

- **Simple**: store decision metadata on the `:HitlSubmission` node:
  - `reviewed_at_ms`, `reviewed_by`, `decision`, `review_notes`
- **Audit-grade**: add event nodes:
  - `(:HitlSubmission)-[:HAS_EVENT]->(:HitlEvent {type, at_ms, notes})`
  - `(:HitlEvent)-[:BY]->(:User)`

Event nodes are better when you expect multiple review cycles, edits, appeals, or future automation. The PROV model explicitly supports representing agents and activities over time. (Source: [W3C PROV-DM](https://www.w3.org/TR/prov-dm/))


### 5) Timestamps (storage vs human readability)

Neo4j supports native temporal types as properties and they support indexing and range queries. (Source: [Neo4j Cypher Manual: Temporal values](https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/))

Your existing schema uses `updated_at: INTEGER`, so a consistent approach is:

- **Store**: `*_at_ms: INTEGER` (epoch millis, UTC)
- **Render for humans in Cypher**: `datetime({epochMillis: *_at_ms})`

Optionally, you can also store a `datetime` property alongside the integer, derived from the integer, if you want it always human-readable in the browser.


### 6) Handling conflicting knowledge (Wikidata inspiration)

If you anticipate multiple competing values/claims, Wikidata’s pattern is instructive:

- keep multiple statements, qualify them, cite references, and mark rank:
  - normal / preferred / deprecated. (Source: [Wikidata Help:Ranking](https://www.wikidata.org/wiki/Help:Ranking))

Wikidata’s data model also emphasizes statements with qualifiers and ranks as first-class concepts. (Source: [Wikidata:Data model](https://www.wikidata.org/wiki/Wikidata:Data_model))

In Neo4j, the analogous approach is:

- represent assertions as nodes (or reify relationships into nodes) and track `rank/status` to decide what is “best” for retrieval.


### 7) Auditing KG writes (later)

Neo4j Change Data Capture (CDC) can capture create/update/delete changes in real time for downstream processing and audit/replication. (Source: [Neo4j CDC docs](https://neo4j.com/docs/cdc/current/))

CDC does not replace HITL semantics (it captures *what* changed, not *why* it was accepted), but it can complement it.


## MVP HITL recommendation (file-first)

Keep MVP minimal while staying compatible with the long-term graph model.

### Identity / provenance (important distinction)

HITL has **two different humans** whose identity should be recorded:

- **Submitter** (Step 1 capture): the person providing feedback in the lookup/chat experience.
  - Captured by the capture MCP: `mcp/hitl_get_feedback/server.py` via `submit_knowledge(..., submitter=...)`.
  - Stored on the pending JSON as top-level `submitter` (required: `name`, `role`).
- **Reviewer / operator** (Step 2 review): the person approving/rejecting submissions.
  - Captured by the review MCP: `mcp/hitl_review/server.py` via `record_review(..., operator_name=..., operator_role=...)`.
  - Stored on the reviewed JSON as `review.operator` (required: `name`, `role`).

### Architecture diagrams

#### Long-term (two-layer HITL + published KG)
```
User (Claude Desktop)
        |
        v
      Agent
        |
        v
 mcp_hitl.submit_knowledge
        |
        v
  +----------------------------------+
  | Proposal + Review layer          |
  | (auditable)                      |
  |                                  |
  | Proposal store                   |
  | (files now; later Neo4j nodes)   |
  |        |                         |
  |        v                         |
  |  Human Operator review           |
  |        |                         |
  |        v                         |
  |  approve / reject (+notes)       |
  +----------------------------------+
        |
        v
 incorporate approved changes
        |
        v
  +----------------------------------+
  | Published KG (query layer)       |
  | Neo4j domain graph               |
  +----------------------------------+
        ^
        |
      Agent
```

#### MVP (step-by-step implementation)
```
Step 1 (done): capture

Agent -> mcp_hitl.submit_knowledge -> HitL_local/pending/<id>.json

Step 2 (next): operator review

HitL_local/pending/<id>.json
        |
        v
   review UI/tools
        |
        v
 approve / reject (+notes)
        |
        v
Later: incorporate into Neo4j KG
```

#### Final (Neo4j: HITL + domain graph in one place)
```
                        files (MVP persistence)
        +-----------------------------------------------+
        |                                               |
        |  HitL_local/pending/*.json   HitL_local/reviewed/**/*.json
        |           |                             |
        |           v                             v
        |      (feedback)                    (review)
        +-----------|-----------------------------|---+
                    |                             |
                    v                             v
            +-----------------+           +-----------------+
            | Neo4j           |           | Neo4j           |
            | (:Feedback)     |<----------| (:Review)       |
            | id, status, ... |  :OF      | decision, ...   |
            +--------+--------+           +--------+--------+
                     |                             |
                     | mentions / about            | mentions / about
          +----------+-----------+-----------------+----------+
          |                      |                            |
          v                      v                            v
   +-------------+        +--------------+              +-------------+
   | (:VMRSCode) |        | (:Vendor)    |              | (:Part)     |
   | code=...    |        | name=...     |              | number=...  |
   +-------------+        +--------------+              +-------------+
```

Notes:
- Pending files become `:Feedback` nodes; reviewed files become `:Review` nodes.
- Both `:Feedback` and `:Review` should be linked to whatever they reference in the JSON (VMRS codes, vendors, parts).

### Current state (implemented)

- Step 1 (capture) MCP server: `mcp/hitl_get_feedback/server.py`
  - Tools: `submit_knowledge`, `get_submission_status`, `list_submissions`
  - Scope: writes pending submissions to `HitL_local/pending/`
- Step 2 (review) MCP server: `mcp/hitl_review/server.py`
  - Tools: `list_submissions`, `get_submission`, `record_review`
  - Scope: approves/rejects submissions and moves files into `HitL_local/reviewed/approved/` or `HitL_local/reviewed/rejected/`
- Claude Desktop MCP config entry: `claude_desktop_config.json` (local machine config)
- Agent-facing guidance (versioned prompts):
  - Lookup agent: `interface prompts/lookup_agent/main_v4.txt`
  - Lookup HITL checklist: `interface prompts/lookup_agent/hitl_feedback_capture_v3.txt`
  - Review agent: `interface prompts/hitl_review_agent/main_v3.txt`

### Near-term plan (step-by-step MVP)

Step 1 (done): capture proposals to `HitL_local/pending/` with strong structured intent.

Step 2 (done): operator review tooling + reviewed/approved/rejected states (file-first), keeping the JSON compatible with a future `:HitlSubmission` node model.

### Storage layout

```
HitL_local/
├── pending/                  # submissions awaiting review
└── reviewed/
    ├── approved/             # reviewed + approved submissions
    └── rejected/             # reviewed + rejected submissions
```

Future (optional):

```
HitL_local/
├── pending/
├── reviewed/        # or split into approved/ rejected/ later
└── conversations/   # only if you later capture extra context explicitly
```


### MVP submission JSON shape (recommended)

Even in files, mirror the future Neo4j node properties:

- `schema_version`: integer (current: `2`)
- `id`: UUID or timestamp+random suffix (so you don’t need `index.json`)
- `type`: correction|addition|context|question
- `status`: `pending` in Step 1
- `submitted_at_ms`: integer epoch millis UTC
- `submitter` (required):
  - `name` (required)
  - `role` (required)
  - optional: `id`, `team`, `channel`, `label`
- `content`:
  - `description` (required)
  - `vmrs_code` (required)
  - `context` (required)
  - `related_query` (required)
  - `target_type?`, `target_key?`, `proposed_action?`, `proposed_payload?` (**strongly recommended** whenever a concrete change is proposed)
  - optional: `context_pack`, `targets`

### Schema (Step 1: pending submission, schema_version=2)

Canonical pending JSON written to: `HitL_local/pending/<id>.json`

```json
{
  "schema_version": 2,
  "id": "HITL-<uuid>",
  "type": "correction",
  "submitted_at_ms": 1737465030000,
  "status": "pending",
  "submitter": {
    "name": "Alex Submitter",
    "role": "Fleet Ops",
    "id": "optional",
    "team": "optional",
    "channel": "optional",
    "label": "optional"
  },
  "content": {
    "vmrs_code": "047-000-000",
    "description": "Short, specific, self-contained description of what should be changed/recorded.",
    "context": "Privacy-safe rationale/evidence. Do NOT paste full transcripts.",
    "related_query": "Exact user question/prompt that triggered this.",
    "target_type": "Component",
    "target_key": { "code": "047-000-000" },
    "targets": [
      { "target_type": "Component", "target_key": { "code": "047-000-000" } }
    ],
    "context_pack": {
      "related_query": "optional duplicate of related_query",
      "answer_excerpt_or_summary": "optional (<= 500 chars)",
      "why_saved": "optional",
      "evidence": [{ "type": "user_claim", "value": "optional" }],
      "expected_vs_observed": { "expected": "optional", "observed": "optional" }
    },
    "proposed_action": "set_property",
    "proposed_payload": { "name": "optional" }
  }
}
```

### MVP review metadata (in reviewed files)

When moving a file from `pending/` to `reviewed/` (Step 2), add:

- `schema_version = 2`
- `status = "reviewed"`
- `review` (canonical):
  - `decision`: approved|rejected
  - `reviewed_at_ms`
  - `notes`
  - `operator` (required):
    - `name` (required)
    - `role` (required)
    - optional: `id`, `team`

For backward compatibility, you may also mirror legacy top-level fields (e.g. `decision`, `reviewed_at_ms`, `review_notes`, `reviewed_by`).

### Schema (Step 2: reviewed submission, schema_version=2)

Canonical reviewed JSON written to:
- `HitL_local/reviewed/approved/<id>.json` or
- `HitL_local/reviewed/rejected/<id>.json`

```json
{
  "schema_version": 2,
  "id": "HITL-<uuid>",
  "type": "correction",
  "submitted_at_ms": 1737465030000,
  "status": "reviewed",
  "submitter": {
    "name": "Alex Submitter",
    "role": "Fleet Ops"
  },
  "content": {
    "vmrs_code": "047-000-000",
    "description": "Short, specific, self-contained description of what should be changed/recorded.",
    "context": "Privacy-safe rationale/evidence.",
    "related_query": "Exact user question/prompt that triggered this."
  },
  "review": {
    "decision": "approved",
    "reviewed_at_ms": 1737469000000,
    "notes": "Why this was approved/rejected (required).",
    "operator": {
      "name": "Jane Operator",
      "role": "Fleet Analyst",
      "id": "optional",
      "team": "optional"
    }
  },
  "decision": "approved",
  "reviewed_at_ms": 1737469000000,
  "review_notes": "Why this was approved/rejected (required).",
  "reviewed_by": "Jane Operator"
}
```


## Sources (cited)

- [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) (provenance core concepts: Entity/Activity/Agent/time)
- [Neo4j BPM modeling example](https://neo4j.com/blog/part-1-using-neo4j-in-business-process-modeling-scenarios/) (Requests, States, lifecycle events)
- [Neo4j Cypher Manual: Temporal values](https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/) (temporal types, epochMillis, indexing/range)
- [Neo4j CDC docs](https://neo4j.com/docs/cdc/current/)
- [Wikidata Help:Ranking](https://www.wikidata.org/wiki/Help:Ranking) (preferred/normal/deprecated semantics)
- [Wikidata:Data model](https://www.wikidata.org/wiki/Wikidata:Data_model) (statements/qualifiers/ranks)

## Working examples (GitHub)

### Python MCP / FastMCP servers

- [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
  - The official SDK repository (note: `main` is v2 pre-alpha; v1.x is the production branch).
  - Useful server examples directory: [examples/snippets/servers](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/snippets/servers)
  - If you want “stable” docs/code, also see the [v1.x branch](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)

### Provenance → Neo4j (PROV-DM import)

- [DLR-SC/prov2neo](https://github.com/DLR-SC/prov2neo) (imports W3C PROV documents into Neo4j)

### Wikidata → Neo4j property graph (statement-heavy KGs)

- [megagonlabs/cypherbench](https://github.com/megagonlabs/cypherbench)
  - Includes a “Wikidata-to-Property-Graph conversion engine” (`wd2neo4j`) that’s useful inspiration if you later want statement-style modeling, provenance subgraphs, etc.

### Approval workflow state machines (inspiration for Step 2+)

- [cjmellor/approval](https://github.com/cjmellor/approval)
  - Laravel package implementing an approval workflow with states like `pending`, `approved`, `rejected` and storing proposed changes as JSON (`new_data`, `original_data`) before applying them.
- [palantir/policy-bot](https://github.com/palantir/policy-bot)
  - GitHub App that enforces approval policies on pull requests (useful inspiration if you later want “approval rules” rather than manual review only).
- [statelyai/xstate](https://github.com/statelyai/xstate)
  - Widely used state machine/statechart library; useful inspiration for explicitly modeling `pending → in_review → approved/rejected` transitions and guards.

