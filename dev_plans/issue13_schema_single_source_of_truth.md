# Issue 13 — Modularize schema: single source of truth

- **GitHub issue**: `https://github.com/Dodhon/vmrs/issues/13`
- **Backlog project**: `Status=Todo`, `Importance=P0`

## End user context
- **Maintainers (Python devs)**: need to evolve the HITL submission/review schema without hunting through MCP servers, prompts, and docs.
- **Prompt authors**: need a single, stable “schema excerpt” to embed/reference in agent prompts.
- **Operators/reviewers**: need consistent fields across captured submissions and reviewed records.

## User requirements
- **Scope clarification**: “Schema” here means the **HITL submission/review JSON shape** (what we write to `HitL_local/.../*.json` and what MCP servers validate/stamp), not the Neo4j domain graph schema.
- **Single change point**: update a field/type/version in exactly one canonical place.
- **No drift**: MCP servers must not duplicate field lists, schema version, or required/optional logic.
- **Prompt-safe schema access**: prompts/docs should reference the canonical schema (or a generated excerpt derived from it).
- **Version stamping**: captured and reviewed JSON must stamp the same `schema_version` from the canonical schema.

## Architecture diagrams

### C4 — Level 1 (System Context)
```
                        +----------------------+
                        |  Neo4j (published KG)|
                        |  (future integration)|
                        +----------^-----------+
                                   |
Submitter (Claude Desktop user)    |
            |                      |
            v                      |
        +---+----------------------+-+
        |         VMRS repo         |
        |  - MCP servers (capture)  |
        |  - MCP servers (review)   |
        |  - Canonical HITL schema  |
        |  - Prompts + docs         |
        |  - Local file storage     |
        +---+----------------------+-+
            ^
            |
 Operator / Reviewer (human)
```

### C4 — Level 2 (Containers + data stores)
```
 +-------------------+       imports/uses        +----------------------+
 | mcp/hitl_get_...   | -----------------------> | src/hitl_schema.py    |
 | (capture server)   |                          | (canonical schema)    |
 +---------+---------+                          +----------+-----------+
           |                                                |
           | writes pending JSON                             | renders excerpt
           v                                                v
 +---------------------------+                 +---------------------------+
 | HitL_local/pending/*.json |                 | interface prompts/*.txt   |
 | (local file store)        |                 | docs/*.md dev_plans/*.md  |
 +-------------+-------------+                 | (reference excerpt/path)  |
               |                               +---------------------------+
               | read/move + stamps review
               v
 +-------------------+       imports/uses        +----------------------+
 | mcp/hitl_review    | -----------------------> | src/hitl_schema.py    |
 | (review server)    |                          | (canonical schema)    |
 +---------+---------+                          +----------------------+
           |
           | moves reviewed JSON
           v
 +------------------------------------+
 | HitL_local/reviewed/{approved|...} |
 | (local file store)                 |
 +------------------------------------+
```

## Runtime view (arc42)

### Scenario A — Capture submission (Step 1)
1. Submitter uses the lookup/chat flow and triggers `submit_knowledge(...)`.
2. Capture MCP server validates the request using the canonical schema helpers.
3. Capture MCP server writes `HitL_local/pending/<id>.json` with `schema_version` from the canonical schema.

### Scenario B — Review submission (Step 2)
1. Operator lists pending submissions and selects one for review.
2. Review MCP server loads `HitL_local/pending/<id>.json` and validates it using canonical schema helpers.
3. Review MCP server stamps canonical `schema_version`, adds the `review` object, moves the file to `HitL_local/reviewed/{approved|rejected}/`.

### Scenario C — Schema change (maintenance)
1. Maintainer updates the canonical schema definition (one file).
2. Any generated prompt excerpt is regenerated from the schema source.
3. MCP servers continue to validate and stamp the updated `schema_version` without any additional field-list edits.

## Goals
- Create **one authoritative HITL schema definition** in the repo.
- Ensure both MCP servers **import the schema** for:
  - `schema_version` stamping
  - required/optional field validation
  - constructing the output JSON shape
- Ensure prompts/docs reference **the same source**, directly or via a generated excerpt derived from it.

## Non-goals
- Migrating storage from files to a DB (tracked separately).
- Building a UI for review.
- Full Neo4j incorporation pipeline for approved changes (future work).
- Updating or redefining any **Neo4j domain schema** text/structure in `interface prompts/` (or elsewhere). If prompts mention Neo4j labels/properties, they remain unchanged in this workstream.

## Proposed approach (minimal)

### Canonical schema location
- Add `src/hitl_schema.py` as the single source of truth:
  - `SCHEMA_VERSION: int`
  - definitions for “pending submission” and “reviewed submission”
  - small validation helpers used by MCP servers
  - `render_prompt_schema_excerpt()` that returns a compact, prompt-safe field list

### Refactor touchpoints
- Update `mcp/hitl_get_feedback/server.py`:
  - use `SCHEMA_VERSION` from `src/hitl_schema.py`
  - centralize required fields and validation (stop duplicating field checks)
- Update `mcp/hitl_review/server.py`:
  - use `SCHEMA_VERSION` from `src/hitl_schema.py`
  - validate loaded submissions against the canonical schema before review
- Update prompts/docs to avoid duplicating **HITL JSON** schema text:
  - reference the canonical file path, or
  - reference a generated excerpt file derived from `render_prompt_schema_excerpt()`

### Keep it dependency-light (initial implementation)
- Start with stdlib-only schema definitions + validation helpers (no new dependency required).
- Optionally graduate to JSON Schema generation/validation later if needed (see References).

## Success metrics (incl. testing)
- **Drift check**: `schema_version` exists in exactly one source file and is imported everywhere else.
- **Refactor check**: MCP servers no longer contain duplicated “field list” comments/logic for the schema’s shape.
- **Update check**: renaming a field (e.g., `review_notes` → `notes`) requires editing **one** canonical file + updating tests; no prompt/doc hunting.
- **Tests**:
  - unit tests for schema helper(s) and excerpt rendering
  - a small integration-style test that exercises both MCP servers’ validators against the same canonical schema version

## References
- **C4 model** (System Context + Container diagrams): `https://c4model.com/`
- **arc42 runtime view** (Section 6): `https://docs.arc42.org/section-6`
- **JSON Schema Draft 2020-12** (official): `https://json-schema.org/draft/2020-12`
- **Pydantic JSON Schema** (optional future “schema as code” path): `https://docs.pydantic.dev/latest/concepts/json_schema`

