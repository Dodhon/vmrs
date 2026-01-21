# VMRS Technical Deck — Single Source


## Role, Goal, and Task

- You are an expert in building technical powerpoints, Senior AI Engineer.
- You are creating a power point to explain the project I do to the data science team / copilot team.
- You need to start high level: what is the problem and how do we solve it?
- The goal is to help me refine the powerpoint wording and critiques.
- Your feedback should be slide by slide.

## Audience & Intent
- DS/AI reviewers who want the technical story (data inputs, pipelines, schema, evaluation, and reproducibility).
- Ready to drop into slides: one takeaway per section; visuals = pipeline + schema.

## Data Inputs (ground truth)
- VMRS master (tabular): 66,729 rows → 289 systems; 3,471 assemblies; 35,724 components. Source: 39 markdown handbook files → CSV pipeline.
- Vendor cleaned (3rd-party validated): 20,348 parts; ~373 unclassified VMRS. Some vendor codes not in the handbook → 101 components created during import; 373 unclassified exported.
- Vendor websites (planned): Verified vendor sites for real-time part lookup and pricing. Bypasses knowledge graph, feeds directly to LLM reasoning layer.
- Quality notes: ~4.9% empty descriptions; OCR typos ("Dus"→"Bus", "Salety"→"Safety", etc.).

## Pipelines (two ingestion lanes)
- **Tabular (ground truth)**: `extract_vmrs_to_csv.py` → `combine_vmrs_csv.py` → `validate_vmrs_csv.py` → (optional) `sort_master_csv.py` / `sort_vendor_csv.py`.
- **LLM (non-tabular/OCR noise)**: `text_chunker` (2k tokens, 200 overlap) → `triple_extractor` (Claude Sonnet 4.5, temp=0, strict JSON/salvage) → `graph_builder` (checkpoints, dedup, relationship fixups) → runner `run_ingest_from_file.py`.
- **Merge**: `merge_csv_with_json.py` (CSV precedence, LLM enrich) → `knowledge_graph_output/combined_triple_extraction_and_md_tables.json`.
- **Vendor branch**: `create_vendor_nodes.py` → `refactor_vendor_schema.py` → `fix_orphaned_vendor_parts.py` (creates 101 missing Components, links 721 orphans, exports 373 unclassified).

## Neo4j Schema & Counts (build-guide snapshot)
- Schema: System ← Assembly ← Component (PART_OF); VendorPart → Component (MAPS_TO); Vendor → VendorPart (MANUFACTURES).
- Counts: Systems 227; Assemblies 2,035; Components 35,974; VendorPart 20,339; Vendor 517; PART_OF 38,009; MAPS_TO 19,966; MANUFACTURES 19,083.
- CSV import (fast/accurate): `PYTHONPATH=. python3 scripts/import_csv_to_neo4j.py`.
- JSON/merge import (legacy/optional): `scripts/neo4j_import.py` or downstream loaders.

## Interface Layer
- **MCP connection**: Neo4j ↔ LLM via Model Context Protocol (`mcp-neo4j-cypher`). Enables Claude to query graph directly.
- **LLM Reasoning Layer**: Claude generates Cypher queries, interprets results, handles ambiguity.
- **Context & Prompt Engineering**: System prompts with VMRS hierarchy context, few-shot examples, output formatting.
- **Chatbot UI options**: Claude Desktop (current), Microsoft Copilot Studio (planned enterprise deployment).
- **Operator Feedback loop (planned)**: Operators provide corrections and context (e.g., "this part goes on the fuel system") → updates graph relationships or adds metadata. Knowledge graph grows over time from human feedback.

## Testing & Evaluation
- Acceptance: 80 Qs (`tests/test_questions/test_log.csv` + `tests/test_questions/conversations/*.md` + scoring summary in `tests/test_questions/EVALUATION_SUMMARY.md`).
- Posture: test happy path + failure modes (ambiguity, missing data, OCR/typos).

## Failure Modes & Mitigations
- OCR/typos, empty descriptions → validation reports; LLM path uses strict code validation/salvage; CSV precedence in merge.
- Component ambiguity → hierarchy context; targeted edge-case evaluation within `tests/test_questions`; plan for human-in-loop feedback.
- Vendor-only codes → create Components from vendor data (101 nodes) with provenance; export unclassified (373 rows).
- Hallucination risk → temp=0, schema validation, dedup, CSV-first merge.

## Repro Commands (minimal set)
- Env: `python3 -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt && cp .env.example .env` (fill Anthropic + Neo4j).
- Tabular pipeline: `python3 scripts/data_processing/extract_vmrs_to_csv.py && python3 scripts/data_processing/combine_vmrs_csv.py && python3 scripts/data_processing/validate_vmrs_csv.py`.
- Neo4j (CSV): `PYTHONPATH=. python3 scripts/import_csv_to_neo4j.py`.
- LLM path: `PYTHONPATH=. python3 scripts/run_ingest_from_file.py --input llm_matching/matching_context.md --save-every 10` (add `--start-chunk N` to resume).
- Merge: `PYTHONPATH=. python3 scripts/merge_csv_with_json.py`.
- Vendor: `python3 scripts/create_vendor_nodes.py && python3 scripts/refactor_vendor_schema.py && python3 scripts/fix_orphaned_vendor_parts.py`.
- Tests: see `tests/test_questions/plans/TEST_PLAN.md`.

## Slide Outline (technical cut)
1) Goal/Context (one line)
2) Data inputs & quality
3) Pipeline (tabular lane + LLM lane + merge + vendor branch)
4) Schema & counts (label snapshot)
5) Interface layer (MCP, LLM reasoning, chatbot UI)
6) Demo (grille / flux capacitor / air filter)
7) Evaluation & results (acceptance + targeted edge-case coverage; confidence by level; pricing gap)
8) Failure modes & mitigations
9) Roadmap/next steps (operator feedback loop, metrics/gates, data cleanup, Snowflake)
10) Backup: hierarchy, ETL details, LLM path, vendor linking, testing deep dive, savings detail
