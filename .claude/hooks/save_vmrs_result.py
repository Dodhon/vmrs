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
CONVERSATIONS_DIR = Path(__file__).parent.parent.parent / "tests" / "test_questions" / "conversations"

def extract_test_id(transcript_lines: list[dict]) -> str | None:
    """Extract test_id from the prompt (expects format: [TEST_ID: XX-XXXXX])"""
    for entry in transcript_lines:
        message = entry.get("message", {})
        if message.get("role") == "user":
            content = message.get("content", "")
            if isinstance(content, list):
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            match = re.search(r"\[TEST_ID:\s*([A-Z]{2}-[a-f0-9]+)\]", content)
            if match:
                return match.group(1)
    return None

def save_conversation_file(test_id: str, transcript_lines: list[dict]) -> Path:
    """Save full conversation to a markdown file and return the path."""
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = CONVERSATIONS_DIR / f"{test_id}.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Test: {test_id}\n\n")

        for entry in transcript_lines:
            message = entry.get("message", {})
            role = message.get("role", "")
            content = message.get("content", "")

            if role == "user":
                f.write("## User\n\n")
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            f.write(f"{item.get('text', '')}\n\n")
                        elif item.get("type") == "tool_result":
                            f.write(f"**Tool Result** (`{item.get('tool_use_id', '')}`):\n```json\n{item.get('content', '')}\n```\n\n")
                else:
                    f.write(f"{content}\n\n")

            elif role == "assistant":
                f.write("## Assistant\n\n")
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            f.write(f"{item.get('text', '')}\n\n")
                        elif item.get("type") == "tool_use":
                            f.write(f"**Tool Call** (`{item.get('name', '')}`):\n```json\n{json.dumps(item.get('input', {}), indent=2)}\n```\n\n")
                else:
                    f.write(f"{content}\n\n")

    return file_path

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

    # Use agent_transcript_path for subagent conversations
    transcript_path = hook_input.get("agent_transcript_path")

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

    # Save full conversation to markdown file
    conv_path = save_conversation_file(test_id, transcript_lines)

    # Update CSV with relative path to conversation file
    rel_path = f"tests/test_questions/conversations/{test_id}.md"
    if update_csv(test_id, rel_path):
        print(f"Saved {test_id} -> {conv_path}")

if __name__ == "__main__":
    main()
