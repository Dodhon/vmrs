#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook.

Trigger phrase: "restart claude desktop"

Behavior (macOS only):
- If Claude Desktop is not running: open it.
- If it is running: quit and relaunch it.

The trigger prompt is blocked/erased by returning JSON:
  {"decision":"block","reason":"..."}
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from typing import Iterable


TRIGGER_PHRASE = "restart claude desktop"
APP_NAME_CANDIDATES = ("Claude", "Claude Desktop")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)


def _is_app_running(app_name: str) -> bool:
    # AppleScript: `application "X" is running` prints true/false.
    p = _run(["osascript", "-e", f'application "{app_name}" is running'])
    if p.returncode != 0:
        return False
    return p.stdout.strip().lower() == "true"


def _open_app(app_name: str) -> bool:
    p = _run(["open", "-a", app_name])
    return p.returncode == 0


def _quit_app(app_name: str) -> None:
    # Ignore errors (e.g., if app is mid-quit or AppleScript can’t target it).
    _run(["osascript", "-e", f'tell application "{app_name}" to quit'])


def _first_running_app(candidates: Iterable[str]) -> str | None:
    for name in candidates:
        if _is_app_running(name):
            return name
    return None


def _first_openable_app(candidates: Iterable[str]) -> str | None:
    for name in candidates:
        if _open_app(name):
            return name
    return None


def restart_or_open(app_candidates: Iterable[str], timeout_s: float) -> tuple[str | None, str]:
    """
    Returns (chosen_app_name, action)
    action is one of: "opened", "restarted", "open_failed"
    """
    running = _first_running_app(app_candidates)
    if not running:
        chosen = _first_openable_app(app_candidates)
        return (chosen, "opened" if chosen else "open_failed")

    _quit_app(running)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if not _is_app_running(running):
            break
        time.sleep(0.2)

    # Relaunch the same name first; fallback to trying other candidates.
    if _open_app(running):
        return (running, "restarted")

    chosen = _first_openable_app(app_candidates)
    return (chosen, "restarted" if chosen else "open_failed")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--dry-run", action="store_true")
    args, _unknown = parser.parse_known_args()

    # Don’t attempt Desktop automation in remote environments.
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true":
        return 0

    if platform.system().lower() != "darwin":
        return 0

    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = hook_input.get("prompt", "")
    if not isinstance(prompt, str):
        return 0

    if prompt.strip().lower() != TRIGGER_PHRASE:
        return 0

    if args.dry_run:
        print(json.dumps({"decision": "block", "reason": "Dry run: would restart Claude Desktop."}))
        return 0

    chosen, action = restart_or_open(APP_NAME_CANDIDATES, timeout_s=8.0)
    if action == "open_failed":
        reason = (
            "Could not open Claude Desktop (app name not found). "
            "Edit APP_NAME_CANDIDATES in .claude/hooks/restart_claude_desktop.py."
        )
        print(json.dumps({"decision": "block", "reason": reason}))
        return 0

    print(json.dumps({"decision": "block", "reason": f"Claude Desktop {action} ({chosen})."}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

