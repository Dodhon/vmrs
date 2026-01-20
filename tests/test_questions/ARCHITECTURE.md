# VMRS Testing Architecture

## Overview Diagram

```mermaid
flowchart TB
    subgraph DataSources["Data Sources"]
        VendorCSV["vendor data/checked/<br/>Motors Part Cleanup - Return Data.csv"]
        Neo4j[("Neo4j Knowledge Graph<br/>(VMRS Hierarchy + Vendor Mappings)")]
    end

    subgraph TestGeneration["Test Generation"]
        Generator["generate_test_questions.py"]
        TestLog["test_log.csv<br/>(80 questions, 9 categories)"]
    end

    subgraph TestExecution["Test Execution"]
        ClaudeCode["Claude Code CLI"]
        MCP["Neo4j MCP Server<br/>(v0.8.2)"]
        Subagent["vmrs-test-runner<br/>(Sonnet 4.5)"]
        Hook["save_vmrs_result.py<br/>(SubagentStop hook)"]
    end

    subgraph Artifacts["Test Artifacts"]
        Conversations["conversations/*.md<br/>(80 transcripts)"]
        Summary["EVALUATION_SUMMARY.md"]
        TestPlan["plans/TEST_PLAN.md"]
    end

    VendorCSV -->|"ground truth"| Generator
    Generator -->|"generates"| TestLog

    TestLog -->|"[TEST_ID: XX-XXXXXX] question"| ClaudeCode
    ClaudeCode -->|"spawns"| Subagent
    Subagent -->|"Cypher queries"| MCP
    MCP -->|"reads"| Neo4j

    Subagent -->|"SubagentStop"| Hook
    Hook -->|"writes transcript"| Conversations
    Hook -->|"updates full_conversation"| TestLog

    TestLog -->|"manual scoring"| Summary
```

## Test Execution Flow

```mermaid
sequenceDiagram
    participant Operator
    participant ClaudeCode as Claude Code
    participant Subagent as vmrs-test-runner
    participant MCP as Neo4j MCP
    participant Neo4j as Neo4j DB
    participant Hook as save_vmrs_result.py

    Operator->>ClaudeCode: [TEST_ID: PN-18ba5e] What is the VMRS code for part 2234788PE?
    ClaudeCode->>Subagent: Spawn subagent

    Subagent->>MCP: get_neo4j_schema
    MCP-->>Subagent: Schema response

    Subagent->>MCP: read_neo4j_cypher (MATCH VendorPart...)
    MCP->>Neo4j: Execute Cypher
    Neo4j-->>MCP: Results
    MCP-->>Subagent: Query results

    Subagent-->>ClaudeCode: Final answer with VMRS code
    ClaudeCode->>Hook: SubagentStop event

    Hook->>Hook: Extract TEST_ID from transcript
    Hook->>Hook: Save conversations/PN-18ba5e.md
    Hook->>Hook: Update test_log.csv
```

## Test Categories

```mermaid
pie title Test Distribution (80 total)
    "part_lookup (PN)" : 10
    "vendor_lookup (VP)" : 10
    "description_exact (DE)" : 10
    "description_partial (DP)" : 10
    "hierarchy_navigation (HN)" : 10
    "vendor_mapping (VM)" : 10
    "validation_valid (VV)" : 5
    "validation_invalid (VI)" : 5
    "comparison (CP)" : 10
```

## Component Details

### Data Layer

| Component | Path | Purpose |
|-----------|------|---------|
| Vendor CSV | `vendor data/checked/Motors Part Cleanup - Return Data.csv` | Ground truth for expected answers |
| Neo4j Graph | Remote (via MCP) | VMRS hierarchy + vendor part mappings |

### Test Generation

| Component | Path | Purpose |
|-----------|------|---------|
| Generator | `generate_test_questions.py` | Creates 80 test questions with oracles |
| Test Log | `test_log.csv` | Test cases, expected answers, results |

**Test ID Format**: `{PREFIX}-{SHA256(row_key)[:6]}`

| Category | Prefix | Count | Behavior |
|----------|--------|-------|----------|
| part_lookup | PN | 10 | KNOWN_PRESENT |
| vendor_lookup | VP | 10 | KNOWN_PRESENT |
| description_exact | DE | 10 | KNOWN_PRESENT |
| description_partial | DP | 10 | KNOWN_PRESENT |
| hierarchy_navigation | HN | 10 | KNOWN_PRESENT |
| vendor_mapping | VM | 10 | KNOWN_PRESENT |
| validation_valid | VV | 5 | KNOWN_PRESENT |
| validation_invalid | VI | 5 | KNOWN_ABSENT |
| comparison | CP | 10 | KNOWN_PRESENT |

### Test Execution

| Component | Path | Purpose |
|-----------|------|---------|
| Subagent | `.claude/agents/vmrs-test-runner.md` | Query Neo4j, answer VMRS questions |
| Hook | `.claude/hooks/save_vmrs_result.py` | Capture transcript on SubagentStop |
| MCP Server | Neo4j MCP v0.8.2 | Bridge to Neo4j database |

**Subagent Tools**:
- `mcp__neo4j-aura__get_neo4j_schema`
- `mcp__neo4j-aura__read_neo4j_cypher`

### Test Artifacts

| Artifact | Path | Purpose |
|----------|------|---------|
| Test Log | `test_log.csv` | Cases + results (source of truth) |
| Transcripts | `conversations/*.md` | Full tool calls + responses |
| Summary | `EVALUATION_SUMMARY.md` | Pass/fail by category |
| Plan | `plans/TEST_PLAN.md` | Methodology documentation |

## Pass/Fail Criteria

```mermaid
flowchart LR
    subgraph Scoring["Scoring Rules"]
        A["VMRS Lookups<br/>(PN/VP/DE/DP)"] -->|"expected in top-3"| Pass
        B["Hierarchy<br/>(HN)"] -->|"code appears with context"| Pass
        C["Vendor Mapping<br/>(VM)"] -->|"≥1 part from oracle"| Pass
        D["Validation Valid<br/>(VV)"] -->|"says YES"| Pass
        E["Validation Invalid<br/>(VI)"] -->|"says NO/NOT_FOUND"| Pass
        F["Comparison<br/>(CP)"] -->|"YES/NO matches oracle"| Pass
    end
```

## Current Results

| Category | Pass | Total | Rate |
|----------|------|-------|------|
| part_lookup | 10 | 10 | 100% |
| vendor_lookup | 9 | 10 | 90% |
| description_exact | 10 | 10 | 100% |
| description_partial | 9 | 10 | 90% |
| hierarchy_navigation | 10 | 10 | 100% |
| vendor_mapping | 10 | 10 | 100% |
| validation_valid | 5 | 5 | 100% |
| validation_invalid | 0 | 5 | 0%* |
| comparison | 10 | 10 | 100% |
| **Total** | **73** | **80** | **91.25%** |

*validation_invalid failures are test-design issues (oracle mismatch), not interface defects.
