# VMRS Chatbot Interface Testing Pipeline - Architecture Diagram Prompt

Create a clean, professional 1920×1080 landscape architecture diagram showing the VMRS Chatbot interface testing pipeline with 6 sections arranged in 2 rows.

All text must be horizontal and short (prefer 1–3 words per label). Avoid paragraphs.

## LAYOUT (2 rows, Local Database left)

Left column: Local Database (Validated CSV) on the top row.
Middle band (centered): Test Generation → Test Execution → External Database across the top row.
Middle band bottom: Evidence & Logs (Local) under Test Execution.
Leave the far-left bottom area empty (no section box).

---

## TEST GENERATION / RESULTS (Row 1, Middle band, left, light purple #E8E1F5)

- **Stratified Random Sampling (According to Predefined Patterns)**
- **Test Suite**

---

## TEST EXECUTION (Row 1, Middle band, center, orange #FFD7B0)

- **Claude Code CLI**
- **Claude Sub Agent** (show multiple stacked icons to indicate parallelism)

---

## EXTERNAL DATABASE (Row 1, Middle band, right, light green #DDF2DD)

- **Neo4j Database**

---

## LOCAL DATABASE (Row 1, Left column, light purple #E8E1F5)

- **Validated CSV**

---

## EVIDENCE & LOGS (Local) (Row 2, Middle band, under Test Execution, light yellow #FFF0B8)

- **save_vmrs_result.py**
- **conversations/*.md**

---

---

## DATA FLOW ARROWS (all blue #1F6FEB, orthogonal routing)

- Validated CSV → Stratified Random Sampling (According to Predefined Patterns): "ground truth"
- Stratified Random Sampling (According to Predefined Patterns) → Test Suite: "generates"
- Test Suite → Claude Code CLI: "[TEST_ID] question" 
- Claude Code CLI → Claude Sub Agent: "spawns"
- Neo4j Database → Claude Sub Agent: "Neo4j MCP"
- Claude Sub Agent → save_vmrs_result.py: "hook"
- save_vmrs_result.py → conversations: "writes transcript"
- save_vmrs_result.py → Test Suite: "writes path to transcript"
- Validated CSV → Test Suite: "LLM as Judge"

---

## STYLE REQUIREMENTS

- Light gray background #F2F2F2
- Rounded rectangles with bold section titles at top-left
- White fill + gray border for processes and data stores (cylinders)
- Small circles for merge/junction points
- No arrow crossings in main top-row flow (Local Database → Test Generation → Test Execution → External Database)
- Route any backflow arrows (e.g., Hook/Scoring writing back to the suite/log) around the perimeter to avoid crossing the main top-row flow
- All text readable (no cut-off, wrap if needed)
- Orthogonal (right-angle) arrow routing
- Only include arrows explicitly defined above.
- Do not combine or mix arrows.
- Do not add icons.