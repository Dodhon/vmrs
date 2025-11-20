<!-- c03a3aa6-bc84-4c0b-b43a-9106a6ac6859 7f8bf86d-f40f-4813-a4db-67257874e367 -->
# Plan: Generate VMRS Chatbot Acceptance Test Suite

## 1. Environment & Setup

- [ ] Create `tests/` directory structure.
- [ ] Create `tests/acceptance/` for these specific tests.
- [ ] Add `pytest` and `pandas` to `requirements.txt` if not present.

## 2. Test Data Generation Script

Create a script `tests/acceptance/generate_dataset.py` that:

- [ ] Reads `Motors Part Cleanup - Return Data - Copy.xlsx` (Ground Truth).
- [ ] Reads `knowledge_graph_output/combined_triple_extraction_and_md_tables_codes.csv` (Graph Knowledge).
- [ ] Filters Ground Truth data:
    - Rows must have a valid `VMRS` code.
    - Rows must have a non-empty `DESCRIPTION`.
    - Checks if the `VMRS` code exists in the Graph Knowledge (optional: flag or exclude if missing, to avoid "hallucination" tests for now).
- [ ] Generates Test Cases in JSON format (`test_cases.json`):
    - Structure: `[{ "id": 1, "question": "What is the VMRS code for 'AIR CONDITIONING CONDENSER'?", "expected_code": "001-001-062", "source_term": "AIR CONDITIONING CONDENSER", "type": "vendor_description" }]`
    - Mix of questions derived from `DESCRIPTION` (Vendor term) and `COMPONENT_` (Standard term).

## 3. Acceptance Test Harness

Create `tests/acceptance/test_qa_accuracy.py`:

- [ ] Define a `ChatbotInterface` protocol/stub (e.g., `ask_chatbot(question: str) -> str`).
- [ ] Implement a `pytest` fixture to load `test_cases.json`.
- [ ] Implement a parameterized test that:
    - Takes a test case.
    - Calls `ask_chatbot(case['question'])`.
    - Asserts that `case['expected_code']` is present in the response.
- [ ] Add a "Mock Chatbot" implementation (simple lookup or random) to demonstrate the test runner works.

## 4. Execution

- [ ] Run the generation script to create the artifact.
- [ ] Run `pytest tests/acceptance` to verify the harness.

### To-dos

- [ ] Create scripts/generate_evaluation_qa.py to extract and format QA pairs from the Excel file
- [ ] Run the generation script and validate the output JSON