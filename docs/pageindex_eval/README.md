# PageIndex Evaluation for VMRS (Issue #32)

## Objective and decision
**Objective:** Evaluate whether PageIndex (VectifyAI/PageIndex) is a fit for the VMRS knowledge graph + vendor mapping + HITL workflow.
**Decision owner:** Thupten. **Execution owner:** TBD.
**Decision options:** Adopt, don’t adopt, or hybrid (PageIndex for retrieval only).

---

## 1) What problem PageIndex solves (inputs/outputs)
**Problem addressed:** Retrieval over long, structured documents where vector similarity search is brittle and hard to explain. PageIndex proposes a vectorless, reasoning‑based retrieval approach using a hierarchical “tree index” (ToC‑like structure) and tree search.

**Inputs:**
- PDF documents (`run_pageindex.py --pdf_path ...`) or Markdown documents (`--md_path ...`).
- Requires an OpenAI key for self‑hosted use per the README.

**Outputs:**
- A hierarchical tree JSON with `node_id`, `title`, `start_index`, `end_index`, and optional summaries (README example).
- Retrieval via reasoning over the tree index (tree search) rather than vector similarity.

**Sources:**
- PageIndex README (usage + tree structure): https://github.com/VectifyAI/PageIndex
- PageIndex intro blog (reasoning‑based retrieval): https://pageindex.ai/blog/pageindex-intro

---

## 2) Fit with Neo4j KG + MCP architecture
**Fit assessment:** Partial / layered fit.

- **Neo4j KG:** PageIndex does not natively integrate with Neo4j. It is a document‑retrieval layer; KG remains the system of record for VMRS entities and vendor mappings.
- **MCP:** PageIndex offers an MCP integration endpoint (pageindex.ai/mcp). This could be used to route “document‑level” questions, but it is separate from our MCP HITL tooling (`mcp/hitl_get_feedback/server.py`).
- **Proposed integration pattern:** Use PageIndex as a retrieval assistant over VMRS manuals (source grounding), then link returned sections/pages to VMRS codes stored in Neo4j. This implies a mapping layer between PageIndex node_ids/pages and VMRS code entities.

**Sources:**
- PageIndex MCP page: https://pageindex.ai/mcp
- VMRS HITL capture: `mcp/hitl_get_feedback/server.py`

---

## 3) Traceability / grounding
**What it offers:**
- PageIndex emphasizes explainability and traceability via structured tree nodes and page/section references.
- The API docs show page‑level references are available by prompting the Chat API.

**Gaps / risks:**
- Traceability is to document pages/sections, not VMRS code provenance. Mapping to VMRS codes is still required.
- Markdown‑based tree quality depends on heading structure; PageIndex warns that converted markdown may not preserve hierarchy.

**Sources:**
- Quickstart (page‑level references): https://docs.pageindex.ai/quickstart
- README (tree structure + markdown notes): https://github.com/VectifyAI/PageIndex

---

## 4) Minimal PoC on VMRS datasets
**Goal:** Validate tree generation + retrieval on a small VMRS subset and assess grounding.

**Candidate inputs (repo‑local):**
- `md data/` (VMRS handbook markdown). If hierarchy quality is poor, use source PDFs if available.

**PoC steps (self‑host path):**
1) Pick a small VMRS markdown file with clear headings (≤20 pages of content).
2) Run tree generation:  
   `python3 run_pageindex.py --md_path "md data/<sample>.md"`
3) Inspect generated tree JSON for node hierarchy + summaries.  
4) Ask 3–5 test questions derived from `tests/test_questions/test_log.csv` and request citations/page references.

**Expected output:**
- Tree JSON with node_ids and summaries.
- Answers with cited page/section references.

**Risks:**
- Markdown hierarchy may be unreliable; if so, re‑run with PDFs or pre‑clean headings.

---

## 5) Tradeoffs vs current approach
| Dimension | Current VMRS approach (Neo4j + scripts) | PageIndex | Impact |
|---|---|---|---|
| Retrieval accuracy | Depends on current prompts + KG queries | Claims improved long‑doc retrieval | Potentially positive; needs PoC evidence |
| Traceability | KG entity‑level + dataset provenance | Page/section grounding, but not KG‑native | Partial; still needs mapping |
| Integration effort | Existing pipeline is stable | New retrieval layer + key management | Medium overhead |
| Infra cost | Local pipeline; API costs for LLM extraction | Requires OpenAI API key or PageIndex API | Cost added |
| Maintainability | Owned in repo | External dependency + evolving API | Increased vendor risk |

---

## 6) Recommendation
**Recommendation:** **Hybrid pilot** only if the PoC confirms improved grounding on VMRS manuals. Otherwise, **do not adopt**.

**Rationale:** PageIndex targets the retrieval pain point, but it is not a KG system. It can complement Neo4j for document grounding, yet it introduces dependency risk and does not eliminate the need for KG mapping or HITL workflows.

---

## 7) Next steps (if approved)
1) Run the PoC on one VMRS manual file and document results (owner: TBD). 
2) If grounding improves, define a mapping layer between PageIndex page/section references and Neo4j VMRS codes. 
3) Decide whether to integrate via self‑host or PageIndex API/MCP (with explicit key management + data egress rules).

---

## Appendix: Validation checklist (issue question coverage)
- What problem does PageIndex solve? **Yes** (Section 1)
- Inputs/outputs? **Yes** (Section 1)
- Integration with Neo4j/MCP? **Yes** (Section 2)
- Traceability/grounding? **Yes** (Section 3)
- Minimal PoC? **Yes** (Section 4)
- Tradeoffs? **Yes** (Section 5)
- Recommendation? **Yes** (Section 6)
