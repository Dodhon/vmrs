#!/usr/bin/env python3
"""
Hook script for SubagentStop event.
Parses the vmrs-test-runner transcript and updates test_log.csv.
"""
import csv
import json
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent.parent / "tests" / "test_questions" / "test_log.csv"

def extract_test_id(transcript_lines: list[dict]) -> str | None:
    """Extract test_id from the prompt (expects format: [TEST_ID: XX-XXXXX])"""
    for entry in transcript_lines:
        if entry.get("role") == "user":
            content = entry.get("content", "")
            if isinstance(content, list):
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            match = re.search(r"\[TEST_ID:\s*([A-Z]{2}-[a-f0-9]+)\]", content)
            if match:
                return match.group(1)
    return None

def get_full_conversation(transcript_lines: list[dict]) -> str:
    """Get full conversation as a single string for the CSV."""
    parts = []
    for entry in transcript_lines:
        role = entry.get("role", "")
        content = entry.get("content", "")
        if isinstance(content, list):
            content = " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
        if role and content:
            parts.append(f"[{role.upper()}]: {content}")
    return "\n\n".join(parts)

def update_csv(test_id: str, full_conversation: str):
    """Update the row in test_log.csv matching test_id."""
    if not CSV_PATH.exists():
        return False

    rows = []
    updated = False

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row.get("test_id") == test_id:
                row["full_conversation"] = full_conversation
                updated = True
            rows.append(row)

    if updated:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return updated

def main():
    hook_input = json.load(sys.stdin)
    transcript_path = hook_input.get("transcript_path")

    if not transcript_path:
        sys.exit(0)

    transcript_lines = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                transcript_lines.append(json.loads(line))

    test_id = extract_test_id(transcript_lines)
    if not test_id:
        sys.exit(0)

    full_conversation = get_full_conversation(transcript_lines)
    if update_csv(test_id, full_conversation):
        print(f"Saved {test_id}")

if __name__ == "__main__":
    main()
