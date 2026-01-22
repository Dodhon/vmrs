# AGENTS.md

This file is a reference index. Keep it in sync with `CLAUDE.md`.

## When to update this file (and `CLAUDE.md`)
Update both `AGENTS.md` and `CLAUDE.md` whenever you:
- Add/remove/rename a **key entry point** (scripts, docs, MCP servers, prompts, plans) that you expect to be referenced again.
- Change the **recommended workflow** (e.g., testing location, how Neo4j is built, where prompts live).
- Move or delete a file/folder that’s referenced here (avoid stale paths).
- Introduce a new “source of truth” document (e.g., a new build guide, evaluation summary, or architecture note).

Before finishing a PR, ensure `README.md` is still accurate for the changes included (or at minimum remind the user to confirm whether it needs updating).

### When to update an individual reference entry
For each item under **Primary references** or **Data locations**, update that specific line when:
- **Path changes**: the file/folder is moved/renamed/deleted.
- **Canonical source changes**: a different file becomes the “go-to” source for that topic (supersedes the old one).
- **Purpose changes**: the “when you need X / why” description is no longer accurate.
- **Status changes**: it's deprecated, replaced, or no longer part of the current workflow (remove it rather than leaving stale guidance).

## Plan requirements
Use the Claude skill `planning` for plan requirements and best-practice references: `~/.claude/skills/planning/SKILL.md`. If you cannot use the skill, read the file directly at `~/.claude/skills/planning/SKILL.md`.

## Project overview
VMRS data processing and knowledge graph tooling that links VMRS codes with vendor parts for analysis and Neo4j-backed applications.
End goal: build a knowledge graph that stakeholders can query through a chatbot interface, with a HITL (human-in-the-loop) feedback capture loop for corrections and improvements.

## Primary references
- `README.md` - when you need a high-level overview; why: broad project summary (may lag behind current workflows)
- `/Users/thuptenwangpo/Library/Application Support/Claude/claude_desktop_config.json` - when updating Claude Desktop MCP servers
- `docs/project_context.md` - when you need the current “agent context”; why: up-to-date workflows, assets, and commands
- `docs/KNOWLEDGE_GRAPH_GUIDE.md` - when you need KG ingestion/extraction details; why: end-to-end pipeline guide
- `docs/ORGANIZATION_SUMMARY.md` - when you need repo navigation rationale; why: structure and where things live
- `scripts/README.md` - when running scripts or checking CLI options; why: catalog and usage notes
- `scripts/data_processing/` - when working on CSV extraction/validation; why: pipeline scripts and conventions
- `docs/NEO4J_BUILD_GUIDE.md` - when setting up or rebuilding Neo4j; why: build steps and design decisions
- `docs/analysis/PATTERNS_ANALYSIS.md` - when interpreting VMRS data patterns; why: key insights and trends
- `docs/analysis/LINKING_PATTERNS.md` - when linking VMRS codes to vendor parts; why: mapping strategies
- `docs/analysis/POC_READY_SUBSETS.md` - when assembling proof-of-concept datasets; why: subset definitions
- `tests/test_questions/` - when validating query answers; why: acceptance test harness + transcripts + scoring
- `dev_plans/hitl_plan.md` - when working on HITL scope; why: step-by-step plan and current MVP shape
- `dev_plans/hitl_step3_context_and_operator_metadata.md` - when upgrading HITL context/operator capture; why: defines the minimal context_pack + operator identity schema and rollout steps
- `HitL_local/hitl_design.md` - when aligning HITL MVP with long-term goals; why: architecture + data model notes
- `dev_plans/` - when working on dev plans; why: all plans live in this folder
- `mcp/hitl/server.py` - when changing HITL capture behavior; why: MCP server implementation
- `mcp/hitl_review/server.py` - when changing HITL operator review behavior
- `interface prompts/` - when editing prompts; why: prompts are organized by agent (e.g. `lookup_agent/`, `hitl_review_agent/`)
- `docs/` - when looking for deeper background docs; why: broader project documentation
- `presentations/` - when referencing past presentation versions; why: pptx version history

## Data locations
- `csv data/` - when using processed VMRS tables; why: canonical CSV exports
- `md data/` - when re-extracting from source docs; why: handbook markdown inputs
- `vendor data/` - when updating vendor part sources; why: raw vendor inputs
- `knowledge_graph_output/` - when inspecting LLM extraction results; why: graph JSON outputs
- `eda/` - when reviewing analysis artifacts; why: exploratory outputs
