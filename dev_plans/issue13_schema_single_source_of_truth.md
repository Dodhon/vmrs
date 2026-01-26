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

## Current issues

The following issues in the current codebase motivate this refactoring:

### 1. Schema version duplication
- **Location**: `mcp/hitl_get_feedback/server.py:175` and `mcp/hitl_review/server.py:261`
- **Problem**: `"schema_version": 2` is hardcoded in both MCP servers
- **Risk**: Version drift if one server is updated but not the other, leading to inconsistent schema versions in captured vs reviewed JSON files

### 2. Field validation duplication
- **Location**: `mcp/hitl_get_feedback/server.py:109-148` and `mcp/hitl_review/server.py:212-229`
- **Problem**: Similar validation logic for required fields is duplicated across both servers
- **Risk**: 
  - Inconsistent validation rules between capture and review flows
  - Maintenance burden: changes must be applied in multiple places
  - Higher chance of bugs when validation logic diverges

### 3. No centralized schema definition
- **Problem**: Field lists and structure are embedded in server code with no single place to see the complete schema definition
- **Risk**: 
  - Schema drift: unclear what the "true" schema shape is
  - Difficult to document the schema for prompt authors and maintainers
  - Hard to generate prompt excerpts or documentation automatically

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
                 ^
                 | renders excerpt to
                 |
 +-------------------------------+
 | Prompt/Doc excerpt generator  |
 | writes: interface prompts/    |
 |        hitl_schema_excerpt.txt|
 +-------------------------------+
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
  - write excerpt output to `interface prompts/hitl_schema_excerpt.txt`

### Refactor touchpoints
- Update `mcp/hitl_get_feedback/server.py`:
  - use `SCHEMA_VERSION` from `src/hitl_schema.py`
  - centralize required fields and validation (stop duplicating field checks)
- Update `mcp/hitl_review/server.py`:
  - use `SCHEMA_VERSION` from `src/hitl_schema.py`
  - validate loaded submissions against the canonical schema before review
- Update prompts/docs to avoid duplicating **HITL JSON** schema text:
  - reference the canonical file path, or
  - reference a generated excerpt file derived from `render_prompt_schema_excerpt()` (written to `interface prompts/hitl_schema_excerpt.txt`; regenerated via a helper/CLI in `src/hitl_schema.py`)

### Keep it dependency-light (initial implementation)
- Start with stdlib-only schema definitions + validation helpers (no new dependency required).
- Optionally graduate to JSON Schema generation/validation later if needed (see References).

### CLI + guardrails (explicit)
- Add a `python -m src.hitl_schema` CLI with:
  - `--write-excerpt "interface prompts/hitl_schema_excerpt.txt"` to regenerate the prompt excerpt from the canonical schema.
  - `--check-excerpt "interface prompts/hitl_schema_excerpt.txt"` to verify the checked-in excerpt is up to date (for CI).
  - `--check-version` to assert `SCHEMA_VERSION` is defined only in `src/hitl_schema.py` and imported by both MCP servers.
- Add `make hitl-schema-excerpt` to run `--write-excerpt`; add CI to run `--check-excerpt` and `--check-version`.

## Scope split

### Core PR
- Introduce `src/hitl_schema.py` as the canonical source of truth (`SCHEMA_VERSION`, pending/reviewed definitions, validation helpers, prompt excerpt renderer).
- Wire both MCP servers (`mcp/hitl_get_feedback/server.py`, `mcp/hitl_review/server.py`) to import version/validators and remove hardcoded schema bits.
- Generate a single prompt excerpt from the canonical source and reference it (write to `interface prompts/hitl_schema_excerpt.txt`), with a deterministic CLI/Make target to regenerate and a CI check that fails if the excerpt is stale.
- Add guardrails: a check that `SCHEMA_VERSION` is defined only once and that MCP servers import it from the canonical module; add unit tests for validators/excerpt rendering and a small integration test that exercises both MCP servers’ validators against shared fixtures.
- Update `AGENTS.md` and `CLAUDE.md` to point to the canonical schema module and excerpt so references stay in sync.

### Optional follow-ups
- Add canonical pending/reviewed JSON fixtures (e.g., `tests/fixtures/hitl_pending.json`, `tests/fixtures/hitl_reviewed.json`) for validator/tests reuse beyond the core smoke fixtures.

### Compatibility and ops assumptions
- No migration of existing `HitL_local` files; stale files can be deleted when upgrading.
- GH issue #16 also covers adjacent schema work; keep cross-references aligned.

### Source-of-truth guardrails (clarification)
- Single definition for `SCHEMA_VERSION` lives in `src/hitl_schema.py`; MCP servers must import it (never re-declare).
- Add a lightweight check/test that fails if `SCHEMA_VERSION` appears more than once in the repo or if MCP servers don’t import from the canonical module (prevents drift).
- Excerpt generation path is fixed (`interface prompts/hitl_schema_excerpt.txt`) to avoid scattered copies.

### Validation coverage (explicit scope)
- Pending submission (capture):
  - Required: `type` in {correction, addition, context, question}; `description` (str); `vmrs_code` (str, non-empty); `context` (str); `related_query` (str); `submitter` object with `name` and `role` (non-empty strings).
  - Optional but typed: `target_type` (str), `target_key` (dict), `targets` (list of dicts), `context_pack` (dict with `answer_excerpt_or_summary` <= 500 chars), `proposed_action` (str), `proposed_payload` (dict).
  - Top-level: `id` (UUID string), `submitted_at_ms` (int), `status` (literal "pending"), `content` object, `schema_version` from canonical.
  - Extra fields: default to rejecting unknown top-level fields to prevent drift; optionally allow a `legacy_extra` object for forward-compat fields when running a migration/cleanup path.
- Reviewed submission (review):
  - Required inputs: `submission_id` matches file; `outcome` in {approved, rejected}; `review_notes` (str); `reviewed_by` (str); `operator_name` (str); `operator_role` (str).
  - Optional inputs: `operator_id` (str), `operator_team` (str).
  - Review block written: `review` object with `decision`, `reviewed_at_ms` (int), `notes`, `operator {name, role, id?, team?}`; plus mirrored legacy fields (`decision`, `reviewed_at_ms`, `review_notes`, `reviewed_by`).
  - Top-level status transitions: pending -> reviewed; `schema_version` stamped from canonical.
  - Extra fields: same policy as pending — reject unknowns by default; optionally accept a dedicated `legacy_extra` object during cleanup/migration.

### Legacy data handling
- Legacy `HitL_local` files can be removed; validators hard-fail on unknown/legacy fields. Remediation is to delete or rewrite stale files; no auto-migration path.

### Testing hooks (to be scheduled)
- Separate GitHub issue to add two minimal test runners (one per HITL MCP server), patterned after `.claude/agents/vmrs-test-runner.md`, so each agent can be exercised in isolation. (User to file; note exists here for tracking.)

## Success metrics (incl. testing)
- **Drift check**: `schema_version` exists in exactly one source file and is imported everywhere else.
- **Refactor check**: MCP servers no longer contain duplicated “field list” comments/logic for the schema’s shape.
- **Update check**: renaming a field (e.g., `review_notes` → `notes`) requires editing **one** canonical file + updating tests; no prompt/doc hunting.
- **Tests**:
  - unit tests for schema helper(s), excerpt rendering (positive + stale excerpt failure), and rejection of unknown fields
  - a small integration-style test that exercises both MCP servers’ validators against the same canonical schema version, including a negative case for unknown fields and status transitions

## References
- **C4 model** (System Context + Container diagrams): `https://c4model.com/`
- **arc42 runtime view** (Section 6): `https://docs.arc42.org/section-6`
- **JSON Schema Draft 2020-12** (official): `https://json-schema.org/draft/2020-12`
- **Pydantic JSON Schema** (optional future “schema as code” path): `https://docs.pydantic.dev/latest/concepts/json_schema`

