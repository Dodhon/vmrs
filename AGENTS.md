# AGENTS.md

This file is a reference index. Keep it in sync with `CLAUDE.md`.

## Project overview
VMRS data processing and knowledge graph tooling that links VMRS codes with vendor parts for analysis and Neo4j-backed applications.
End goal: build a knowledge graph that stakeholders can query through a chatbot interface.

## Primary references
- `README.md` - when you need the project overview or quick start steps; why: defines scope and entry points
- `scripts/README.md` - when running scripts or checking CLI options; why: catalog and usage notes
- `scripts/data_processing/README.md` - when working on CSV extraction/validation; why: pipeline details
- `docs/NEO4J_BUILD_GUIDE.md` - when setting up or rebuilding Neo4j; why: build steps and design decisions
- `docs/analysis/PATTERNS_ANALYSIS.md` - when interpreting VMRS data patterns; why: key insights and trends
- `docs/analysis/LINKING_PATTERNS.md` - when linking VMRS codes to vendor parts; why: mapping strategies
- `docs/analysis/POC_READY_SUBSETS.md` - when assembling proof-of-concept datasets; why: subset definitions
- `tests/test_questions/` - when validating query answers; why: acceptance test harness + transcripts + scoring
- `dev_plans/hitl_plan.md` - when working on HITL scope; why: step-by-step plan and current MVP shape
- `HitL_local/hitl_design.md` - when aligning HITL MVP with long-term goals; why: architecture + data model notes
- `mcp/hitl/server.py` - when changing HITL capture behavior; why: MCP server implementation
- `interface prompts/hitl_feedback_capture.txt` - when tuning HITL capture quality; why: what to include in submissions
- `docs/` - when looking for deeper background docs; why: broader project documentation
- `writing_guides/` - when writing or polishing presentation materials; why: reference PDFs
- `presentations/` - when referencing past presentation versions; why: pptx version history

## Data locations
- `csv data/` - when using processed VMRS tables; why: canonical CSV exports
- `md data/` - when re-extracting from source docs; why: handbook markdown inputs
- `vendor data/` - when updating vendor part sources; why: raw vendor inputs
- `knowledge_graph_output/` - when inspecting LLM extraction results; why: graph JSON outputs
- `eda/` - when reviewing analysis artifacts; why: exploratory outputs
