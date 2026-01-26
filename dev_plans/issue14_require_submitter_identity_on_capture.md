# Plan: Issue #14 — Require submitter name + role during HITL capture

## Links
- Issue #14: HITL lookup_agent: require operator name + role during feedback capture
- Capture guidance prompt: `interface prompts/lookup_agent/hitl_feedback_capture_v3.txt`
- Lookup agent prompt: `interface prompts/lookup_agent/main_v4.txt`
- Capture MCP server: `mcp/hitl_get_feedback/server.py`

## Goal
Make HITL submissions more **auditable** by having the lookup/capture flow **ask** for:
- `submitter.name`
- `submitter.role`

For MVP, allow the user/operator to say “skip” and proceed with placeholders (e.g., name="Unknown", role="unspecified") so capture remains low-friction while still satisfying server validation.

## Non-goals
- Review-side operator identity collection (that is HITL review agent behavior).
- Changing HITL storage format or schema beyond minor prompt-level additions.

## Current state
- Server-side validation already requires `submitter.name` and `submitter.role` (it will reject/reprompt if missing).
- The prompts mention this requirement, but do not explicitly instruct the agent to ask the user for these fields when missing.

## Proposed changes
1) Update `interface prompts/lookup_agent/hitl_feedback_capture_v3.txt`
- Add a short “Required-field collection” note:
  - If submitter identity isn’t available, ask for it (one question, constrained format).
  - Provide a canonical format for the answer (name + role; optional id/team).

2) Update `interface prompts/lookup_agent/main_v4.txt`
- Strengthen the HITL section to explicitly require asking for submitter identity when missing.

## Test plan
Manual:
- Run the integration runner (or the lookup agent) with a HITL capture scenario where submitter identity is not provided.
- Confirm the agent asks for submitter name/role before submitting.
- Confirm `submit_knowledge` succeeds and a pending JSON is written.

## Acceptance criteria
- Capture flow asks the user/operator for submitter identity (name + role) before submitting.
- If the user/operator says “skip”, capture still proceeds using placeholders that satisfy validation (e.g., name="Unknown", role="unspecified").
- The prompts provide a consistent, low-friction way for a human operator to supply identity.
