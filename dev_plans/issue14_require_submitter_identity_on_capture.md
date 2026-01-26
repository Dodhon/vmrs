# Plan: Issue #14 — Require submitter name + role during HITL capture

## Links
- Issue #14: HITL lookup_agent: require operator name + role during feedback capture
- Capture guidance prompt: `interface prompts/lookup_agent/hitl_feedback_capture_v4.txt`
- Lookup agent prompt: `interface prompts/lookup_agent/main_v5.txt`
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
1) Add `interface prompts/lookup_agent/hitl_feedback_capture_v4.txt`
- Keep `v3` immutable.
- Add MVP guidance to ask for submitter identity but allow “skip” with placeholders.

2) Add `interface prompts/lookup_agent/main_v5.txt`
- Keep `v4` immutable.
- Update the HITL section to reference `hitl_feedback_capture_v4.txt` and include the “ask but allow skip” behavior.

## Test plan
Manual:
- Run the integration runner (or the lookup agent) with a HITL capture scenario where submitter identity is not provided.
- Confirm the agent asks for submitter name/role before submitting.
- Confirm `submit_knowledge` succeeds and a pending JSON is written.

## Acceptance criteria
- Capture flow asks the user/operator for submitter identity (name + role) before submitting.
- If the user/operator says “skip”, capture still proceeds using placeholders that satisfy validation (e.g., name="Unknown", role="unspecified").
- The prompts provide a consistent, low-friction way for a human operator to supply identity.
