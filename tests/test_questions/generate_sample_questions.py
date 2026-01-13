#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")
NUMBERED_RE = re.compile(r"^\d+\.\s+(.*)$")
PATTERN_RE = re.compile(r"^pattern\s+\d+:", re.IGNORECASE)


def clean_text(text: str) -> str:
    text = ZERO_WIDTH_RE.sub("", text)
    text = text.strip()
    return re.sub(r"\s+", " ", text)


def extract_question(line: str) -> str | None:
    raw = line.strip()
    if not raw:
        return None

    is_numbered = False
    match = NUMBERED_RE.match(raw)
    if match:
        is_numbered = True
        raw = match.group(1)

    if "?" not in raw and not is_numbered:
        return None

    raw = re.sub(r"\*\*(.*?)\*\*", r"\1", raw)
    raw = raw.split(" - ", 1)[0]
    return clean_text(raw)


def parse_questions(markdown_text: str) -> list[dict[str, str]]:
    category = "Uncategorized"
    pattern = None
    questions = []

    for raw_line in markdown_text.splitlines():
        line = clean_text(raw_line)
        if not line:
            continue

        if line.startswith("## "):
            category = line.lstrip("# ").strip()
            pattern = None
            continue

        if PATTERN_RE.match(line):
            pattern = line
            continue

        if line.startswith("#"):
            continue

        question = extract_question(raw_line)
        if not question:
            continue

        questions.append(
            {
                "category": pattern or category,
                "question": question,
            }
        )

    return questions


def generate_samples(
    questions: list[dict[str, str]],
    max_count: int | None,
    shuffle: bool,
    seed: int | None,
) -> list[dict[str, str]]:
    items = list(questions)
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(items)
    if max_count is not None:
        items = items[:max_count]
    return items


def write_output(
    questions: list[dict[str, str]], output_path: Path, output_format: str
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "txt":
        content = "\n".join(item["question"] for item in questions) + "\n"
        output_path.write_text(content, encoding="utf-8")
        return

    payload = {
        "count": len(questions),
        "questions": questions,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    default_input = Path(__file__).with_name("questions.md")
    default_output = Path(__file__).with_name("sample_questions.json")

    parser = argparse.ArgumentParser(
        description=(
            "Generate sample questions from tests/test_questions/questions.md."
        )
    )
    parser.add_argument("--input", type=Path, default=default_input)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument(
        "--format", choices=["json", "txt"], default="json"
    )
    parser.add_argument("--max", type=int, default=None)
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--seed", type=int, default=None)

    args = parser.parse_args()
    markdown_text = args.input.read_text(encoding="utf-8")
    questions = parse_questions(markdown_text)
    samples = generate_samples(questions, args.max, args.shuffle, args.seed)
    write_output(samples, args.output, args.format)

    print(f"Wrote {len(samples)} questions to {args.output}")


if __name__ == "__main__":
    main()
