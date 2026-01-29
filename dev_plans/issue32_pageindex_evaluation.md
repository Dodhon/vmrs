# Issue 32 — Evaluate PageIndex (VectifyAI/PageIndex) for VMRS

## 0) Executive Summary (5–10 lines)
**Objective & Ask:** Produce a grounded evaluation of PageIndex for the VMRS KG + vendor mapping + HITL workflow and decide whether to adopt, reject, or pursue a hybrid; decision owner: Thupten. Execution owner: TBD. Target decision date: [TODO].
**Context:** VMRS relies on long-form manuals, vendor data, and a Neo4j-backed KG with HITL capture; retrieval quality and traceability are critical. PageIndex proposes a vectorless, reasoning-based retrieval model that claims better explainability and page-level traceability. 
**Problem:** We need to know whether PageIndex fits our data formats, integrates with the KG/MCP architecture, and offers measurable benefits over current retrieval. 
**Proposal:** Run a structured evaluation: (1) technical fit review, (2) minimal PoC on a VMRS subset, (3) tradeoff analysis vs current pipeline, (4) recommendation write-up. 
**Benefits:** Clear adopt/reject decision, explicit integration options, and quantified tradeoffs (cost, complexity, maintainability, grounding fidelity).
**Ask:** Approve this plan so I can execute the evaluation steps and produce the final write-up in `docs/` or `dev_plans/`.

## 1) End‑user context
- **Primary user:** Thupten (technical lead), building a VMRS knowledge graph and HITL workflow.
- **Secondary users:** Internal stakeholders who need grounded, traceable answers about VMRS codes and vendor parts.
- **Goals:** Higher retrieval accuracy for long documents, explicit traceability (page/section), minimal integration overhead, and compatibility with current Neo4j + MCP workflows.

## 2) Requirements (R1..Rn)
- **R1 — Problem fit:** Identify what PageIndex solves (inputs/outputs, retrieval model, traceability claims). 
- **R2 — Integration fit:** Determine how PageIndex could integrate with Neo4j-backed KG and MCP agent architecture.
- **R3 — Traceability:** Evaluate support for citations, source pages, and provenance for VMRS answers.
- **R4 — PoC feasibility:** Define a minimal PoC on existing VMRS data (`md data/`, `vendor data/`, `tests/test_questions/`).
- **R5 — Tradeoffs:** Compare PageIndex to the current approach (complexity, cost, maintainability).
- **R6 — Recommendation:** Deliver a short, actionable recommendation with next steps.

## 3) Non‑goals
- Building a full production integration.
- Replacing the Neo4j KG or rewriting existing ingestion pipelines.
- Benchmarking against multiple third‑party RAG systems beyond PageIndex.

## 4) Success metrics
- **S1:** Write‑up answers all issue questions with explicit citations to sources.
- **S2:** A minimal PoC plan is concrete, reproducible, and scoped to ≤1–2 documents.
- **S3:** Tradeoff matrix with ≥5 dimensions (accuracy, traceability, infra cost, integration effort, maintainability).
- **S4:** Clear recommendation (adopt / don’t adopt / hybrid) with explicit next steps.

## 5) Current repo state (repo‑grounded)
- **Knowledge graph build**: `docs/NEO4J_BUILD_GUIDE.md` documents the Neo4j schema and ingest pipeline; System/Assembly/Component, VendorPart, Vendor nodes and relationships (PART_OF, MAPS_TO, MANUFACTURES).
- **KG extraction pipeline**: `docs/KNOWLEDGE_GRAPH_GUIDE.md` details the LLM‑assisted extraction workflow and outputs under `knowledge_graph_output/`.
- **HITL capture**: `mcp/hitl_get_feedback/server.py` (per README) + `interface prompts/lookup_agent/hitl_feedback_capture.txt` define the HITL submission flow and schema; `HitL_local/pending/` stores pending submissions.
- **Data sources**: `md data/` (VMRS handbook markdown), `vendor data/checked/` (cleaned vendor parts), and `tests/test_questions/` (QA artifacts).

## 6) Architecture / system impact diagram (ASCII)
```
CURRENT (simplified)

VMRS md data + vendor data
        |
        v
Extraction scripts (scripts/...) -> knowledge_graph_output/ -> Neo4j (System/Assembly/Component/VendorPart)
        |
        v
Agent + MCP (hitl_get_feedback) -> HitL_local/pending

PROPOSED (evaluation / hybrid candidate)

VMRS md data (subset)
        |
        v
PageIndex tree (vectorless index) -> PageIndex retrieval (tree search)
        |                                   |
        |                                   v
        |                              Grounded answer + page/section refs
        v
Neo4j KG (optional) <---- mapping layer to link PageIndex nodes to VMRS codes
        |
        v
HITL capture (unchanged) -> HitL_local/pending
```

## 7) Assumptions & constraints
- PageIndex open‑source repo and docs are accessible (no paywall). 
- PageIndex SDK/API requires API keys (if cloud); self‑host path requires Python deps and OpenAI key per README.
- We will **not** follow any instructions from external repos unless explicitly approved by Thupten (prompt‑injection guard).
- Evaluation will use small subsets to control cost/time.

## 8) Work breakdown (E1..En) mapping to R*
- **E1 — Source review & capability mapping (R1, R2, R3)**
  - Artifacts: summary of PageIndex capabilities, input/output formats, traceability features.
  - Sources: PageIndex README + docs + blog.
  - Touchpoints: `docs/` evaluation write‑up.
  - Owner: TBD. Time window: TBD.

- **E2 — Integration fit analysis (R2, R3)**
  - Artifacts: integration options matrix (self‑host vs API vs MCP); compatibility with Neo4j + MCP.
  - Touchpoints: `docs/` evaluation write‑up.
  - Owner: TBD. Time window: TBD.

- **E3 — Minimal PoC design (R4)**
  - Artifacts: concrete PoC steps with commands and sample input/output expectations.
  - Touchpoints: `docs/` evaluation write‑up.
  - Owner: TBD. Time window: TBD.

- **E4 — Tradeoff analysis (R5)**
  - Artifacts: tradeoff table vs current VMRS pipeline (accuracy, traceability, infra cost, complexity, maintenance).
  - Touchpoints: `docs/` evaluation write‑up.
  - Owner: TBD. Time window: TBD.

- **E5 — Recommendation & next steps (R6)**
  - Artifacts: explicit recommendation + staged next steps.
  - Touchpoints: `docs/` evaluation write‑up.
  - Owner: TBD. Time window: TBD.

## 9) Validation plan (V1..Vn) mapping to R* + success metrics
- **V1 (R1/R3):** Verify PageIndex’s input/output and traceability claims from official docs.
  - Command: `web_fetch https://raw.githubusercontent.com/VectifyAI/PageIndex/main/README.md` and `web_fetch https://docs.pageindex.ai/quickstart`.
  - Expected: documented tree structure, retrieval flow, and page/section references.
  - Failure: missing or ambiguous I/O/traceability details.

- **V2 (R4):** Validate minimal PoC steps are runnable on VMRS markdown subset.
  - Command (example): `python3 run_pageindex.py --md_path "md data/<sample>.md"` (self‑host path per README).
  - Expected: generated tree output (JSON) with node_ids + summaries.
  - Failure: no tree output or unsupported markdown input (explicitly note fallback to PDF path).

- **V3 (R5):** Tradeoff matrix includes ≥5 dimensions and references current repo docs.
  - Check: table includes accuracy/grounding, infra cost, complexity, maintainability, integration effort.
  - Expected: each dimension has a short evidence note.
  - Failure: fewer than five dimensions or missing evidence.

- **V4 (R6/S1–S4):** Final write‑up answers all issue questions and includes recommendation + next steps.
  - Check: explicit sections for problem fit, integration fit, traceability, PoC, tradeoffs, recommendation.
  - Failure: missing any required issue question.

## 10) Risks & mitigations
- **Risk:** PageIndex requires paid API keys or cloud access; self‑host may require OpenAI key.
  - **Mitigation:** Plan includes both self‑host and API evaluation options; note cost assumptions explicitly.
- **Risk:** Markdown hierarchy is unreliable for VMRS `md data/` (PageIndex warns about conversion artifacts).
  - **Mitigation:** Use source PDFs if available, or validate Markdown structure before PoC; document fallback.
- **Risk:** Integration with Neo4j/KG requires mapping between PageIndex nodes and VMRS codes.
  - **Mitigation:** Include explicit mapping approach (node_id ↔ VMRS code) in PoC design or mark as open question.

## 11) Top 10 reader questions (with answers or explicit follow‑up)
1. **What does PageIndex actually output?** → README and docs show a JSON tree index with node_id, title, start/end index, summary (source: PageIndex README + blog). 
2. **Does it support markdown inputs?** → README documents `--md_path` with heading‑based tree; caveat on conversion quality.
3. **Can it provide page/section citations?** → Docs state page‑level references can be prompted (Quickstart).
4. **How does it integrate with MCP?** → PageIndex provides MCP integration endpoint (pageindex.ai/mcp); assess compatibility with existing MCP tooling.
5. **Is it compatible with our Neo4j KG?** → Only via a mapping layer; not natively graph‑aware (to be evaluated in E2).
6. **What is the minimal PoC?** → One VMRS markdown or PDF input → PageIndex tree → sample queries with citations.
7. **What are the costs?** → Self‑host requires OpenAI key; cloud API requires PageIndex API key; both need cost estimates.
8. **What does it replace?** → Retrieval layer only; it does not replace Neo4j KG or HITL capture.
9. **Does it help vendor mapping?** → Potentially for grounding from manuals; vendor mapping still likely uses KG + rules.
10. **What’s the recommendation?** → Will be based on PoC results + tradeoff matrix.

## 12) Open questions
- Do we have source PDFs for the VMRS manuals, or only markdown conversions?
- Is PageIndex allowed to call external APIs in our environment for evaluation? (keys + policy)
- Do we want to evaluate purely self‑host or include API/MCP options?

## 13) Core PR vs Optional follow‑ups
- **Core PR (must‑do):** Evaluation write‑up + recommendation in `docs/` or `dev_plans/`.
- **Optional follow‑ups:** If promising, draft an integration spike plan or a more formal benchmark against current retrieval.

## 14) Recommendation
Proceed with the evaluation as structured above, using official PageIndex documentation and a small VMRS subset to validate feasibility and traceability. This yields a decision‑ready write‑up with minimal risk and no irreversible changes.

## 15) Next steps
1. Confirm preferred output location: `docs/` vs `dev_plans/` (owner: Thupten; date: [TODO]).
2. Approve whether to include API/MCP evaluation or keep to self‑host only (owner: Thupten; date: [TODO]).
3. Upon approval, execute E1–E5 and deliver the write‑up.

---

## Decision contracts
- **Retrieval semantics:** PageIndex retrieval is reasoning‑based over a tree index; if adopted, retrieval decisions are driven by node selection not vector similarity.
- **Truth source:** Neo4j remains the system of record for VMRS entities; PageIndex is an auxiliary retrieval layer unless explicitly promoted.
- **Deployment semantics:** Any use of PageIndex (self‑host vs API) must specify key management, data egress boundaries, and rollback to current retrieval.

## Current vs proposed schema/interface
- **Current:** No PageIndex integration; retrieval relies on existing scripts and Neo4j queries.
- **Proposed:** Add evaluation documentation only. If later adopted, introduce a mapping interface between PageIndex tree node IDs and VMRS codes (schema TBD).

## State machine semantics (not applicable)
No new workflow state machine introduced in this evaluation. Any future integration should define terminal vs non‑terminal states for retrieval, validation, and HITL correction.

## WAF‑lite non‑functional posture
- **Principals / auth boundary:** PageIndex API keys (if used) must be scoped and stored outside the repo; no credentials in code.
- **Security/privacy:** VMRS manuals may be proprietary; ensure PageIndex usage complies with data handling requirements (TBD).
- **Reliability:** Evaluation assumes best‑effort; production adoption would require SLAs and fallback to current retrieval.
- **Ops/observability:** For any integration, log retrieval node_ids and page references for auditability.
- **Performance:** Expect tree generation time proportional to document length; measure on a single doc.
- **Cost posture:** Use smallest possible doc subset; estimate per‑doc costs if API is used.

## Path assumptions, schemas, IDs, and error/empty states
- **Repo root:** `/Users/thuptenwangpo/clawd/vmrs`.
- **Inputs:** VMRS markdown in `md data/`; vendor data in `vendor data/checked/`; evaluation prompts in `tests/test_questions/`.
- **Outputs (evaluation docs):** `docs/pageindex_evaluation.md` (proposed) or `dev_plans/issue32_pageindex_evaluation.md` (this plan).
- **IDs:** PageIndex node_id generation is handled by PageIndex; if mapping to VMRS codes, define a deterministic mapping table (TBD).
- **Empty/error states:** If PageIndex cannot parse markdown structure, fall back to PDF inputs or mark PoC as blocked with explicit reason.

## References (best‑practice / official docs)
- PageIndex README (capabilities, CLI): https://github.com/VectifyAI/PageIndex
- PageIndex Quickstart (SDK/API): https://docs.pageindex.ai/quickstart
- PageIndex framework blog: https://pageindex.ai/blog/pageindex-intro
- PageIndex MCP page: https://pageindex.ai/mcp
- VMRS KG build guide: `docs/NEO4J_BUILD_GUIDE.md`
- VMRS KG guide: `docs/KNOWLEDGE_GRAPH_GUIDE.md`

---

## Ready for Execution
- [ ] Output location decided (`docs/` vs `dev_plans/`).
- [ ] Evaluation scope approved (self‑host only vs API/MCP included).
- [ ] At least one VMRS document identified for the PoC.
- [ ] External API key policy confirmed (if needed).
- [ ] Decision date set by Thupten.
