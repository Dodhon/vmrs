# HITL Design Notes (Long-term + MVP)

## What HITL is doing (first principles)

A human-in-the-loop (HITL) system for a knowledge graph has two different responsibilities:

- **Capture proposals about the world** (messy, conflicting, incomplete, sometimes wrong).
- **Maintain a current working graph state** (useful defaults for queries, but revisable).

Long-term, this pushes you toward **two layers**:

1. **Proposal / review layer** (auditable; ideally append-only-ish)
2. **Published KG layer** (the current `System/Assembly/Component/Vendor/VendorPart` graph users query)

This is consistent with provenance thinking: provenance records **entities, activities, agents, and time** so users can judge trustworthiness and responsibility. (Source: `https://www.w3.org/TR/prov-dm/`)


## Long-term Neo4j model (recommended)

### 1) Store HITL as first-class nodes

Create a node like:

- `(:HitlSubmission { id, type, status, description, context?, related_query?, submitted_at_ms, ... })`

Rationale: review is a workflow (pending → reviewed/approved/rejected). Neo4j’s workflow/state modeling example uses Requests, States, and lifecycle metadata to answer operational questions (“what’s pending”, “who approved”, “what notes”). (Source: `https://neo4j.com/blog/part-1-using-neo4j-in-business-process-modeling-scenarios/`)


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

Event nodes are better when you expect multiple review cycles, edits, appeals, or future automation. The PROV model explicitly supports representing agents and activities over time. (Source: `https://www.w3.org/TR/prov-dm/`)


### 5) Timestamps (storage vs human readability)

Neo4j supports native temporal types as properties and they support indexing and range queries. (Source: `https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/`)

Your existing schema uses `updated_at: INTEGER`, so a consistent approach is:

- **Store**: `*_at_ms: INTEGER` (epoch millis, UTC)
- **Render for humans in Cypher**: `datetime({epochMillis: *_at_ms})`

Optionally, you can also store a `datetime` property alongside the integer, derived from the integer, if you want it always human-readable in the browser.


### 6) Handling conflicting knowledge (Wikidata inspiration)

If you anticipate multiple competing values/claims, Wikidata’s pattern is instructive:

- keep multiple statements, qualify them, cite references, and mark rank:
  - normal / preferred / deprecated. (Source: `https://www.wikidata.org/wiki/Help:Ranking`)

Wikidata’s data model also emphasizes statements with qualifiers and ranks as first-class concepts. (Source: `https://www.wikidata.org/wiki/Wikidata:Data_model`)

In Neo4j, the analogous approach is:

- represent assertions as nodes (or reify relationships into nodes) and track `rank/status` to decide what is “best” for retrieval.


### 7) Auditing KG writes (later)

Neo4j Change Data Capture (CDC) can capture create/update/delete changes in real time for downstream processing and audit/replication. (Source: `https://neo4j.com/docs/cdc/current/`)

CDC does not replace HITL semantics (it captures *what* changed, not *why* it was accepted), but it can complement it.


## MVP HITL recommendation (file-first)

Keep MVP minimal while staying compatible with the long-term graph model.

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
  |   Operator review                |
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

### Current state (implemented)

- MCP server: `mcp/hitl/server.py`
  - Tools: `submit_knowledge`, `get_submission_status`, `list_submissions`
  - Scope: **pending-only capture** (writes to `HitL_local/pending/`)
- Claude Desktop MCP config entry: `claude_desktop_config.json` (local machine config)
- Agent-facing guidance:
  - `interface prompts/hitl_feedback_capture.txt` (what to include; intent fields are strongly recommended)
  - `interface prompts/main_v3.txt` references HITL and when to use it

### Near-term plan (step-by-step MVP)

Step 1 (done): capture proposals to `HitL_local/pending/` with strong structured intent.

Step 2 (next): add operator review tooling + reviewed/approved/rejected states (file-first), keeping the JSON compatible with a future `:HitlSubmission` node model.

### Storage layout

```
HitL_local/
└── pending/         # submissions awaiting review (MVP writes here)
```

Future (not required for Step 1, but recommended when review tooling is added):

```
HitL_local/
├── pending/
├── reviewed/        # or split into approved/ rejected/ later
└── conversations/   # only if you later capture extra context explicitly
```


### MVP submission JSON shape (recommended)

Even in files, mirror the future Neo4j node properties:

- `id`: UUID or timestamp+random suffix (so you don’t need `index.json`)
- `type`: correction|addition|context|question
- `status`: `pending` in Step 1; later `reviewed` / `approved` / `rejected`
- `submitted_at_ms`: integer epoch millis UTC
- `content`:
  - `description` (required)
  - `vmrs_code?`, `context?`, `related_query?`
  - `target_type?`, `target_key?`, `proposed_action?`, `proposed_payload?` (**strongly recommended** whenever a concrete change is proposed)

### MVP review metadata (in reviewed files)

When moving a file from `pending/` to `reviewed/` (Step 2), add:

- `reviewed_at_ms`
- `decision`: approved|rejected (or reviewed_only for a transitional phase)
- `review_notes`
- `reviewed_by`


## Sources (cited)

- W3C PROV-DM (provenance core concepts: Entity/Activity/Agent/time): `https://www.w3.org/TR/prov-dm/`
- Neo4j workflow/state modeling example (Requests, States, lifecycle events): `https://neo4j.com/blog/part-1-using-neo4j-in-business-process-modeling-scenarios/`
- Neo4j temporal values (temporal types, epochMillis, indexing/range): `https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/`
- Neo4j CDC overview: `https://neo4j.com/docs/cdc/current/`
- Wikidata ranking (preferred/normal/deprecated semantics): `https://www.wikidata.org/wiki/Help:Ranking`
- Wikidata data model (statements/qualifiers/ranks): `https://www.wikidata.org/wiki/Wikidata:Data_model`

