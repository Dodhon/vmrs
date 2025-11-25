# AI Agent Context

## Mission
- Build and validate a dependable bridge between VMRS standards and vendor part data so stakeholders can ask questions (via an MCP-connected Neo4j agent) and trust the answers.
- Prioritize verifiable outputs over UI work; acceptance testing is focused on the Q&A layer, not the chatbot shell.

## High-Value Resources
- `README.md`: end-to-end overview, key metrics (66,729 VMRS codes, 29,710 vendor parts, 93.7% linkage success), PoC datasets, next steps.
- `scripts/README.md`: canonical description of every data-processing script plus knowledge-graph ingestion tooling.
- `docs/analysis/*.md`: pattern analysis, linking strategies, PoC dataset notes.
- `ORGANIZATION_SUMMARY.md`: rationale for current structure and navigation tips.

## Core Pipelines
1. **VMRS preparation**: `extract_vmrs_to_csv.py` → `combine_vmrs_csv.py` → `validate_vmrs_csv.py` → `sort_master_csv.py`.
2. **Vendor prep**: `excel_to_csv.py` (Excel → CSV) → `sort_vendor_csv.py`.
3. **Linkage & scoring outputs**: curated CSVs in `eda/` (`vendor_vmrs_matched_codes.csv`, `poc_dataset.csv`, `perfect_alignment_poc.csv`) capture historic linkage analyses; treat them as provided reference datasets.
4. **Knowledge graph ingestion**: `run_ingest_from_file.py` / `run_graph_extraction.py` chunk VMRS context (e.g., `llm_matching/matching_context.md`) into JSON + Neo4j, using Anthropic + optional Neo4j credentials.

## Critical Data Assets
- `csv data/VMRS_COMPLETE_v20_MASTER.csv`: single source of truth for VMRS hierarchy.
- `vendor data/Master Parts list for Richard 06.25.25 (1).csv`: 29,710 vendor parts (derived from Excel via scripts); sorted variants live alongside it.
- `vendor data/checked/Motors Part Cleanup - Return Data.csv`: stakeholder-designated ground truth for acceptance tests.
- `knowledge_graph_output/combined_triple_extraction_and_md_tables_codes.csv`: merged result of LLM triple extraction (for narrative sections) plus structured table extraction from the official VMRS handbook; this is what currently lives in Neo4j.
- `knowledge_graph_output/combined_triple_extraction_1_and_2.json`: raw export from the extraction runs (useful for rehydrating the KG).
- `eda/vendor_vmrs_matched_codes.csv`, `eda/poc_dataset.csv`, `eda/perfect_alignment_poc.csv`: matched/graded outputs for demos (System 044 focus + cross-system set).

### Reliability Notes
- Vendor-supplied VMRS codes were inconsistent, so the handbook became the ground truth. Treat handbook-derived data as authoritative, and use vendor codes only after verifying against handbook references or the KG.
- The KG’s source chain is: official handbook (tabular + narrative) → LLM triple extraction + table ingestion → `combined_triple_extraction_and_md_tables_codes.csv` → Neo4j. Document any future refreshes so agents know which run produced the active graph.

## Triple Extraction Workflow
1. **Chunk + extract narrative text**: `run_ingest_from_file.py` (or `run_graph_extraction.py`) slices `md data/*.md`, feeds each chunk to Anthropic for triple extraction (System, Assembly, Component, PART_OF), and accumulates JSON (`knowledge_graph_output/combined_triple_extraction_1_and_2.json`).
2. **Convert to reviewable CSVs**: `python3 scripts/convert_extraction_to_csv.py` turns the JSON run artifacts into entity-specific CSVs so we can diff runs or hand-audit descriptions before import.
3. **Merge table data**: Handbook sections that already contain structured tables are exported separately and merged with the triple output to create `knowledge_graph_output/combined_triple_extraction_and_md_tables_codes.csv` (this is the file loaded into Neo4j).
4. **Optional Neo4j load**: Re-run `run_ingest_from_file.py` with Neo4j credentials or use `import_hierarchy_to_neo4j.py` when you need to push refreshed CSVs into the graph.

## Knowledge Graph & QA Scope
- Chatbot questions must resolve through Neo4j; acceptance tests should simulate stakeholder prompts such as “What is the VMRS code for a mirror actuator?” or “Which assemblies span multiple systems?”
- Use the MCP-enabled agent to query the graph, but validate answers against vendor ground truth (`vendor data/checked/...`) when possible.
- Ensure every test case states: (a) question, (b) data path(s) consulted, (c) expected answer/constraints, (d) verification method.
- The Neo4j graph is populated from LLM-extracted triples (Systems ↔ Assemblies ↔ Components). Maintain awareness of hierarchy when formulating checks.

## Stakeholder Expectations & Process Notes
- Treat **PART**, **MANUFACTURER**, and **DESCRIPTION** from David’s CSV as the authoritative columns; any mapping work should align to `matching_context.md`.
- Before executing, create and critique a plan (“planning mode”); reason → act loops (ReAct) are encouraged for traceability.
- Strive for agile delivery: break summary/matching/QA work into bite-sized tasks, sync with stakeholders on “what we have vs. what’s missing,” and capture any methodology shared by subject-matter experts.
- Acceptance testing should include LLM-driven unit-style checks that enforce strict input/output formats and confirm the QA agent mirrors stakeholder review steps.

## Immediate Focus
- Flesh out the acceptance test suite described in `prompts/test_case_prompt.txt`, ensuring coverage of common stakeholder questions and any single-source-of-truth datasets.

## Quick Commands
```bash
# Prep vendor + VMRS data
python3 scripts/data_processing/extract_vmrs_to_csv.py
python3 scripts/data_processing/combine_vmrs_csv.py
python3 scripts/data_processing/validate_vmrs_csv.py
python3 scripts/data_processing/excel_to_csv.py

# Knowledge graph ingestion (requires .env with Anthropic + optional Neo4j creds)
PYTHONPATH=. python3 scripts/run_ingest_from_file.py --input llm_matching/matching_context.md
```

