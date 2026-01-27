## Summary
(What is changing and why? 1–5 bullets.)

## Related
- Related: #<issue-number>
  - Use **Fixes/Closes #<issue-number>** only if merging this PR should auto-close the issue.

## Checklist (minimum bar)
- [ ] Linked to the appropriate issue (Related / Fixes/Closes)
- [ ] If this is an *initial plan PR* for an issue:
  - [ ] included a `dev_plans/` plan file and linked it here
  - [ ] plan includes a **“Current repo state”** section grounded in a quick recon (e.g., existing `.github/workflows/*`, relevant `dev_plans/`, code paths, tests)
- [ ] If this PR touches `interface prompts/`: did not edit old versioned prompts in place; added a new `*_vN+1` file and updated references
- [ ] Added a short verification note (how to test / what to check)

## Verification
- (Commands run, screenshots, or specific steps to validate.)

## Notes (optional)
- Risks / rollout / follow-ups / out-of-scope
