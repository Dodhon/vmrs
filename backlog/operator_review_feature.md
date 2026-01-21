# Operator Review Feature (Backlog)

## Summary
Add MCP tools for fleet team operators to review, approve, or reject user submissions.

## Tools to Add
| Tool | Description |
|------|-------------|
| `get_pending_reviews` | List submissions awaiting review |
| `get_submission_detail` | View full submission details |
| `approve_submission` | Approve with optional notes |
| `reject_submission` | Reject with required reason |
| `edit_and_approve` | Modify content then approve |
| `get_review_stats` | Review progress statistics |

## Storage Changes
Add folders to `HitL_local/`:
- `approved/` - Approved submissions
- `rejected/` - Rejected submissions
- `incorporated/` - Applied to knowledge graph

## Schema Addition
Add review metadata to submission JSON:
```json
"review": {
  "reviewed_at": "2026-01-21T14:00:00",
  "reviewed_by": "operator_name",
  "decision": "approved|rejected",
  "notes": "Review notes"
}
```

## Depends On
- HITL User Submission Feature (dev_plans/hitl_plan.md)
