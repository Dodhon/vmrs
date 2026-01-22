# Restart Claude Desktop via Claude Code Hook (macOS)

## End user context
You’re a local developer using **Claude Desktop** with MCP servers. When you add a new MCP server (by editing `claude_desktop_config.json`), the Desktop app often needs a full restart to re-read config and reset connections.

You want a quick “voice-command-like” trigger: type **`restart claude desktop`** and have a hook do the restart automatically.

## User requirements
- When you submit the exact prompt **`restart claude desktop`**, a hook should:
  - quit Claude Desktop
  - re-open Claude Desktop
  - work regardless of whether Claude Desktop is currently running:
    - if closed: open Claude Desktop
    - if open: restart it (quit + relaunch)
  - prevent that prompt from being processed as a normal request (so it doesn’t pollute the session)
- Minimal implementation first (macOS-only is fine).
- Should be easy to adjust if the app bundle name differs (e.g., `"Claude"` vs `"Claude Desktop"`).

## Goals
- Provide a single, deterministic trigger phrase (`restart claude desktop`) that restarts (or opens) Claude Desktop on macOS.
- Ensure the trigger prompt is blocked/erased and does not become part of the conversation context.
- Keep the implementation small, project-local, and easy to remove/disable.

## Non-goals
- Cross-platform support (Windows/Linux).
- Automatically detecting whether `claude_desktop_config.json` changed.
- Restarting Claude Code / the CLI itself.
- Managing MCP server definitions (this plan only restarts the Desktop app).

## Success metrics
- Submitting `restart claude desktop` results in Claude Desktop being open within ~10 seconds (open if closed, quit+relaunch if open).
- The submitted trigger prompt is not processed as a normal request (it is blocked/erased; no assistant response content is generated from it).
- After restart/open, Claude Desktop reconnects to MCP servers (manual visual confirmation in Desktop UI).

## Key references (what we’re relying on)
- Claude Code hooks support `UserPromptSubmit` and can **block prompt processing** using structured JSON output and/or `continue=false`. (Docs: `https://code.claude.com/docs/en/hooks`)
- Claude Code snapshots hooks at startup; changes require review in `/hooks` and won’t affect an already-running session until restarted. (Docs: `https://code.claude.com/docs/en/hooks`)

## Architecture diagram
```
You (type: "restart claude desktop")
        |
        v
Claude Code session
  UserPromptSubmit hook
        |
        v
.claude/hooks/restart_claude_desktop.py (or .sh)
        |
        v
macOS: quit Claude.app -> wait -> open Claude.app
        |
        v
Claude Desktop restarts -> MCP connections reset
```

## Proposed minimal design
### Script (project-local)
Create a project-local hook script at `/.claude/hooks/restart_claude_desktop.py` (or `.sh`) that:
- reads hook input JSON from `stdin`
- checks `prompt` (case-insensitive, trimmed) == `"restart claude desktop"`
- if not matching: exit 0 quickly (no output)
- if matching:
  - run a restart sequence on macOS:
    - detect whether Claude Desktop is running
      - if not running: `open -a` to launch
      - if running: `osascript` to quit -> wait/poll (bounded timeout) -> `open -a` to relaunch
  - print JSON to stdout to halt further processing (exit code 0):
    - `{"decision":"block","reason":"Restarting Claude Desktop..."}` (blocks/erases the prompt)

Why JSON + `continue=false`:
- For `UserPromptSubmit`, this prevents the submitted prompt from being processed downstream. (Docs: `https://code.claude.com/docs/en/hooks`)

### Hook wiring (project-local and safe-by-default)
Add a `UserPromptSubmit` hook entry.

Recommended location:
- Put this hook in `.claude/settings.local.json` (machine-specific, not committed), unless you explicitly want it shared.

Example shape (final content may vary based on your existing file):
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/restart_claude_desktop.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## Implementation steps
1. **Add restart hook script**
   - Create `.claude/hooks/restart_claude_desktop.py`
   - Keep it macOS-only initially; exit 0 on other OSes.
2. **Make it executable** (optional but recommended)
   - `chmod +x .claude/hooks/restart_claude_desktop.py`
3. **Register the hook**
   - Add the `UserPromptSubmit` entry to `.claude/settings.local.json` (preferred) or `.claude/settings.json`.
4. **Apply in Claude Code**
   - Run `/hooks` to review/apply changes (Claude Code won’t hot-load hook edits mid-session).

## Verification
- Edit `claude_desktop_config.json` to add a new MCP server (location reference: `/Users/thuptenwangpo/Library/Application Support/Claude/claude_desktop_config.json`).
- In Claude Code, submit exactly: `restart claude desktop`
- Expected:
  - If Claude Desktop is closed: it opens
  - If Claude Desktop is open: it quits and relaunches
  - the prompt does **not** get processed as a normal request (session continues without a “response” to that prompt beyond the hook’s stop reason)
  - MCP servers appear/reconnect in Claude Desktop after restart

## Risks / notes
- **App name mismatch**: `open -a "Claude"` may need to be changed to match your installed bundle name.
- **Security**: hooks run automatically; keep the script small and deterministic.
- **Hook runtime**: avoid long waits; implement a bounded timeout for the “wait until quit” loop.

