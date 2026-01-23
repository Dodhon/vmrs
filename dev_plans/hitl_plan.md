# HITL Feedback Capture (MVP)

## Overview
MCP server that lets Claude Desktop users submit **structured feedback** (corrections/additions/questions) for later review.

Notes:
- Claude Desktop does **not** expose full chat transcripts to MCP tools automatically; for now we store **feedback only**.
- Operator review/approval is part of the MVP goal, but we’re implementing it **step-by-step**:
  - Step 1 (current): pending-only capture to `HitL_local/pending/`
  - Step 2 (next): operator review/approval tooling + reviewed state

## Repo layout (new)
```
mcp/hitl_get_feedback/
├── server.py            # MCP server implementation
```

Prompt guidance (used by the Claude Desktop agent):
- `interface prompts/lookup_agent/hitl_feedback_capture.txt`

## Local storage layout
```
HitL_local/
├── pending/                # New submissions awaiting review (MVP writes here)
├── reviewed/               # Reviewed submissions (empty for now)
└── conversations/          # Conversation context/logs (empty for now)
```

## IDs + timestamps (MVP decisions)
- **ID**: no `index.json`. Use a collision-resistant ID (recommended: `uuid4` or timestamp+random suffix).
  - File naming: `HitL_local/pending/<id>.json`
- **Time**: store `submitted_at_ms` as **epoch millis UTC** (integer). This aligns with the existing Neo4j model’s `updated_at: INTEGER`.

## Diagrams

### Long-term HITL architecture (target state)
```
User (Claude Desktop)
        |
        v
      Agent
        |
        v
 mcp_hitl.submit_knowledge
        |
        v
  +-------------------------------+
  | Proposal / Review layer       |
  | (auditable)                   |
  |                               |
  | store submission              |
  | (files now; later Neo4j node) |
  |        |                      |
  |        v                      |
  |   operator review             |
  |        |                      |
  |        v                      |
  |  approve / reject (+notes)    |
  +-------------------------------+
        |
        v
 incorporate approved changes
        |
        v
  +-------------------------------+
  | Published KG (query layer)    |
  | Neo4j domain graph:           |
  | System/Assembly/Component/... |
  +-------------------------------+
        ^
        |
      Agent
```

### MVP (pending-only capture you just built)
```
User (Claude Desktop)
        |
        v
      Agent
        |
        v
  feedback worth saving?
     |           |
    no          yes
     |           |
     v           v
    End   mcp_hitl.submit_knowledge
                  |
                  v
   write JSON -> HitL_local/pending/<id>.json
                  |
                  v
        return submission id to chat
```

## Submission schema (MVP)
```json
{
  "id": "HITL-<uuid_or_timestamp>",
  "type": "correction|addition|context|question",
  "submitted_at_ms": 1737465030000,
  "status": "pending",
  "content": {
    "vmrs_code": "047-000-000",
    "description": "What the user wants to record",
    "context": "Why this is valuable",
    "related_query": "Query that prompted this",

    "target_type": "Component|VendorPart",
    "target_key": {"code": "047-000-000"},
    "proposed_action": "set_property|add_relationship|remove_relationship",
    "proposed_payload": {"name": "New official name"}
  }
}
```

## Review metadata (future)
When review tooling is added later, store review decision metadata alongside the submission:
```json
{
  "reviewed_at_ms": 1737469000000,
  "decision": "approved|rejected",
  "review_notes": "Why this was approved/rejected",
  "reviewed_by": "operator_name_or_id"
}
```

## MCP tools (MVP)
| Tool | Description |
|------|-------------|
| `submit_knowledge` | Create a new pending submission file and return the new ID |
| `get_submission_status` | Check pending status by ID |
| `list_submissions` | List recent pending submissions (no per-user identity in MVP) |

## Files to create
- `mcp/hitl_get_feedback/server.py`
- `HitL_local/pending/`
- `interface prompts/lookup_agent/hitl_feedback_capture.txt`

## Implementation (MVP)
1. Create `HitL_local/pending/`
2. Build MCP server in `mcp/hitl_get_feedback/server.py` (Python MCP SDK / `FastMCP`)
3. Add a Claude Desktop MCP entry pointing to `mcp/hitl_get_feedback/server.py` (via `claude_desktop_config.json`)
4. Put the agent-facing guidance in `interface prompts/lookup_agent/hitl_feedback_capture.txt` and reference it from your main interface prompt as needed.

## Verification (MVP)
1. Run `python3 mcp/hitl_get_feedback/server.py`
2. Call `submit_knowledge` with test data
3. Verify JSON created in `HitL_local/pending/` and `submitted_at_ms` is present
4. Call `get_submission_status` with the returned ID
