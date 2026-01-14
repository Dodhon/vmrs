#!/usr/bin/env python3
"""Generate test questions from vendor CSV data with machine-generated oracle answers.

This script creates test questions for VMRS code validation testing. Questions are
generated from verified vendor-to-VMRS mappings and include expected answers (oracles)
for automated grading.

Output aligns with tests/test_questions/TEST_PLAN.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import random
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple


# Constants
DEFAULT_VENDOR_CSV = Path("vendor data/checked/Motors Part Cleanup - Return Data.csv")
OUTPUT_PATH = Path("tests/test_questions/test_log.csv")
SEED = 42

# Category prefixes for test IDs
PREFIXES = {
    "part_lookup": "PN",
    "vendor_lookup": "VP",
    "description_exact": "DE",
    "description_partial": "DP",
    "hierarchy_navigation": "HN",
    "vendor_mapping": "VM",
    "validation_valid": "VV",
    "validation_invalid": "VI",
    "comparison": "CP",
}

# Question counts per category
COUNTS = {
    "part_lookup": 10,
    "vendor_lookup": 10,
    "description_exact": 10,
    "description_partial": 10,
    "hierarchy_navigation": 10,
    "vendor_mapping": 10,
    "validation_valid": 5,
    "validation_invalid": 5,
    "comparison": 10,
}


class VendorRow(NamedTuple):
    """A row from the vendor CSV."""

    part: str
    manufacturer: str
    description: str
    vmrs: str
    system: str
    assembly: str
    component: str
    row_key: str


class TestQuestion(NamedTuple):
    """A generated test question with oracle data."""

    test_id: str
    category: str
    expected_behavior: str
    question_text: str
    row_key: str
    expected_answer: str
    vendor_parts: str


def compute_row_key(part: str, manufacturer: str) -> str:
    """Compute row key as PART|MANUFACTURER."""
    return f"{part}|{manufacturer}"


def generate_test_id(category: str, row_key: str) -> str:
    """Generate stable test ID from category prefix and row_key hash."""
    prefix = PREFIXES[category]
    hash_hex = hashlib.sha256(row_key.encode()).hexdigest()[:6]
    return f"{prefix}-{hash_hex}"


def load_vendor_csv(csv_path: Path) -> list[VendorRow]:
    """Load vendor CSV and return list of VendorRow objects."""
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            part = row.get("PART", "").strip()
            vmrs = row.get("VMRS", "").strip()
            if not part or not vmrs:
                continue

            vendor_row = VendorRow(
                part=part,
                manufacturer=row.get("MANUFACTURER", "").strip(),
                description=row.get("DESCRIPTION", "").strip(),
                vmrs=vmrs,
                system=row.get("SYSTEM_", "").strip(),
                assembly=row.get("ASSEMBLY_", "").strip(),
                component=row.get("COMPONENT_", "").strip(),
                row_key=compute_row_key(part, row.get("MANUFACTURER", "").strip()),
            )
            rows.append(vendor_row)
    return rows


def build_indexes(
    rows: list[VendorRow],
) -> tuple[dict[str, set[str]], dict[str, list[tuple[str, str]]]]:
    """Build lookup indexes for ambiguity detection.

    Returns:
        part_to_vmrs: Map each PART to set of VMRS codes it maps to
        vmrs_to_parts: Map each VMRS to list of (PART, MANUFACTURER) tuples
    """
    part_to_vmrs: dict[str, set[str]] = defaultdict(set)
    vmrs_to_parts: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for row in rows:
        part_to_vmrs[row.part].add(row.vmrs)
        vmrs_to_parts[row.vmrs].append((row.part, row.manufacturer))

    return dict(part_to_vmrs), dict(vmrs_to_parts)


def select_diverse(
    rows: list[VendorRow], count: int, rng: random.Random, key_attr: str = "system"
) -> list[VendorRow]:
    """Select rows with diverse values for the given attribute.

    Cycles through different attribute values to avoid clustering.
    """
    # Group rows by the key attribute
    by_key: dict[str, list[VendorRow]] = defaultdict(list)
    for row in rows:
        key_value = getattr(row, key_attr) or "UNKNOWN"
        by_key[key_value].append(row)

    # Shuffle within each group
    for group in by_key.values():
        rng.shuffle(group)

    # Cycle through groups to select diverse rows
    selected = []
    keys = list(by_key.keys())
    rng.shuffle(keys)
    key_idx = 0

    while len(selected) < count and any(by_key.values()):
        key = keys[key_idx % len(keys)]
        if by_key[key]:
            selected.append(by_key[key].pop())
        key_idx += 1
        # Remove exhausted keys
        keys = [k for k in keys if by_key[k]]
        if not keys:
            break

    return selected[:count]


def generate_part_lookup(
    rows: list[VendorRow],
    part_to_vmrs: dict[str, set[str]],
    rng: random.Random,
) -> list[TestQuestion]:
    """Generate part_lookup questions using unambiguous part numbers."""
    # Filter to unambiguous parts (map to exactly one VMRS)
    unambiguous = [r for r in rows if len(part_to_vmrs[r.part]) == 1]

    # Deduplicate by part number (keep first occurrence)
    seen_parts: set[str] = set()
    unique_rows = []
    for row in unambiguous:
        if row.part not in seen_parts:
            seen_parts.add(row.part)
            unique_rows.append(row)

    selected = select_diverse(unique_rows, COUNTS["part_lookup"], rng)

    questions = []
    for row in selected:
        questions.append(
            TestQuestion(
                test_id=generate_test_id("part_lookup", row.row_key),
                category="part_lookup",
                expected_behavior="KNOWN_PRESENT",
                question_text=f"What is the VMRS code for part number {row.part}?",
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts="",
            )
        )
    return questions


def generate_vendor_lookup(
    rows: list[VendorRow], rng: random.Random
) -> list[TestQuestion]:
    """Generate vendor_lookup questions with diverse manufacturers."""
    selected = select_diverse(rows, COUNTS["vendor_lookup"], rng, "manufacturer")

    questions = []
    for row in selected:
        questions.append(
            TestQuestion(
                test_id=generate_test_id("vendor_lookup", row.row_key),
                category="vendor_lookup",
                expected_behavior="KNOWN_PRESENT",
                question_text=(
                    f"What is the VMRS code for {row.manufacturer} part {row.part}?"
                ),
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts="",
            )
        )
    return questions


def generate_description_exact(
    rows: list[VendorRow], rng: random.Random
) -> list[TestQuestion]:
    """Generate description_exact questions with unique descriptions."""
    # Filter to rows with non-empty descriptions
    with_desc = [r for r in rows if r.description]

    # Deduplicate by description
    seen_desc: set[str] = set()
    unique_rows = []
    for row in with_desc:
        if row.description not in seen_desc:
            seen_desc.add(row.description)
            unique_rows.append(row)

    selected = select_diverse(unique_rows, COUNTS["description_exact"], rng)

    questions = []
    for row in selected:
        questions.append(
            TestQuestion(
                test_id=generate_test_id("description_exact", row.row_key),
                category="description_exact",
                expected_behavior="KNOWN_PRESENT",
                question_text=f'What is the VMRS code for "{row.description}"?',
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts="",
            )
        )
    return questions


def generate_description_partial(
    rows: list[VendorRow], rng: random.Random
) -> list[TestQuestion]:
    """Generate description_partial questions with truncated descriptions."""
    # Filter to rows with descriptions of 3+ words
    multi_word = [r for r in rows if len(r.description.split()) >= 3]

    # Deduplicate by description
    seen_desc: set[str] = set()
    unique_rows = []
    for row in multi_word:
        if row.description not in seen_desc:
            seen_desc.add(row.description)
            unique_rows.append(row)

    selected = select_diverse(unique_rows, COUNTS["description_partial"], rng)

    questions = []
    for row in selected:
        words = row.description.split()
        partial_desc = " ".join(words[: len(words) - 1])
        questions.append(
            TestQuestion(
                test_id=generate_test_id("description_partial", row.row_key),
                category="description_partial",
                expected_behavior="KNOWN_PRESENT",
                question_text=f'What is the VMRS code for "{partial_desc}"?',
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts="",
            )
        )
    return questions


def generate_hierarchy_navigation(
    rows: list[VendorRow], rng: random.Random
) -> list[TestQuestion]:
    """Generate hierarchy_navigation questions for unique VMRS codes."""
    # Deduplicate by VMRS code
    seen_vmrs: set[str] = set()
    unique_rows = []
    for row in rows:
        if row.vmrs not in seen_vmrs:
            seen_vmrs.add(row.vmrs)
            unique_rows.append(row)

    selected = select_diverse(unique_rows, COUNTS["hierarchy_navigation"], rng)

    questions = []
    for row in selected:
        questions.append(
            TestQuestion(
                test_id=generate_test_id("hierarchy_navigation", row.row_key),
                category="hierarchy_navigation",
                expected_behavior="KNOWN_PRESENT",
                question_text=f"What is the hierarchy for VMRS code {row.vmrs}?",
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts="",
            )
        )
    return questions


def generate_vendor_mapping(
    rows: list[VendorRow],
    vmrs_to_parts: dict[str, list[tuple[str, str]]],
    rng: random.Random,
) -> list[TestQuestion]:
    """Generate vendor_mapping questions for VMRS codes with 2+ parts."""
    # Find VMRS codes with multiple parts
    multi_part_vmrs = {v: parts for v, parts in vmrs_to_parts.items() if len(parts) >= 2}

    # Get representative rows for each such VMRS
    vmrs_rows = {}
    for row in rows:
        if row.vmrs in multi_part_vmrs and row.vmrs not in vmrs_rows:
            vmrs_rows[row.vmrs] = row

    candidate_rows = list(vmrs_rows.values())
    rng.shuffle(candidate_rows)
    selected = candidate_rows[: COUNTS["vendor_mapping"]]

    questions = []
    for row in selected:
        parts_list = vmrs_to_parts[row.vmrs]
        expected_parts = ";".join(f"{p}|{m}" for p, m in parts_list)
        questions.append(
            TestQuestion(
                test_id=generate_test_id("vendor_mapping", row.row_key),
                category="vendor_mapping",
                expected_behavior="KNOWN_PRESENT",
                question_text=f"What vendor parts map to VMRS code {row.vmrs}?",
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts=expected_parts,
            )
        )
    return questions


def generate_validation_valid(
    rows: list[VendorRow], rng: random.Random
) -> list[TestQuestion]:
    """Generate validation_valid questions for valid VMRS codes."""
    # Deduplicate by VMRS code
    seen_vmrs: set[str] = set()
    unique_rows = []
    for row in rows:
        if row.vmrs not in seen_vmrs:
            seen_vmrs.add(row.vmrs)
            unique_rows.append(row)

    rng.shuffle(unique_rows)
    selected = unique_rows[: COUNTS["validation_valid"]]

    questions = []
    for row in selected:
        questions.append(
            TestQuestion(
                test_id=generate_test_id("validation_valid", row.row_key),
                category="validation_valid",
                expected_behavior="KNOWN_PRESENT",
                question_text=f"Is {row.vmrs} a valid VMRS code?",
                row_key=row.row_key,
                expected_answer=row.vmrs,
                vendor_parts="",
            )
        )
    return questions


def generate_validation_invalid(
    rows: list[VendorRow], rng: random.Random
) -> list[TestQuestion]:
    """Generate validation_invalid questions with perturbed VMRS codes."""
    # Collect all valid VMRS codes
    valid_vmrs = {row.vmrs for row in rows}

    # Get some VMRS codes to perturb
    vmrs_list = list(valid_vmrs)
    rng.shuffle(vmrs_list)

    invalid_codes = []
    for vmrs in vmrs_list:
        if len(invalid_codes) >= COUNTS["validation_invalid"]:
            break

        # Try to perturb the last digit
        parts = vmrs.split("-")
        if len(parts) == 3:
            last = parts[2]
            if last.isdigit():
                # Try incrementing/decrementing
                for delta in [1, -1, 2, -2]:
                    new_last = str(int(last) + delta).zfill(len(last))
                    new_vmrs = f"{parts[0]}-{parts[1]}-{new_last}"
                    if new_vmrs not in valid_vmrs:
                        invalid_codes.append((vmrs, new_vmrs))
                        break

    questions = []
    for original, invalid in invalid_codes:
        row_key = f"INVALID|{invalid}"
        questions.append(
            TestQuestion(
                test_id=generate_test_id("validation_invalid", row_key),
                category="validation_invalid",
                expected_behavior="KNOWN_ABSENT",
                question_text=f"Is {invalid} a valid VMRS code?",
                row_key=row_key,
                expected_answer="",
                vendor_parts="",
            )
        )
    return questions


def generate_comparison(
    rows: list[VendorRow],
    vmrs_to_parts: dict[str, list[tuple[str, str]]],
    rng: random.Random,
) -> list[TestQuestion]:
    """Generate comparison questions for same/different VMRS pairs."""
    # Find VMRS codes with multiple parts for same-VMRS comparisons
    multi_part_vmrs = {v: parts for v, parts in vmrs_to_parts.items() if len(parts) >= 2}

    questions = []

    # Generate 5 same-VMRS pairs
    vmrs_list = list(multi_part_vmrs.keys())
    rng.shuffle(vmrs_list)
    same_count = 0
    for vmrs in vmrs_list:
        if same_count >= 5:
            break
        parts = multi_part_vmrs[vmrs]
        if len(parts) >= 2:
            part_a, manuf_a = parts[0]
            part_b, manuf_b = parts[1]
            row_key = f"{part_a}|{manuf_a}+{part_b}|{manuf_b}"
            questions.append(
                TestQuestion(
                    test_id=generate_test_id("comparison", row_key),
                    category="comparison",
                    expected_behavior="KNOWN_PRESENT",
                    question_text=(
                        f"Do parts {part_a} and {part_b} have the same VMRS code?"
                    ),
                    row_key=row_key,
                    expected_answer=f"{vmrs};{vmrs}",
                    vendor_parts="",
                )
            )
            same_count += 1

    # Generate 5 different-VMRS pairs
    all_vmrs = list(vmrs_to_parts.keys())
    rng.shuffle(all_vmrs)
    different_count = 0
    for i in range(len(all_vmrs) - 1):
        if different_count >= 5:
            break
        vmrs_a = all_vmrs[i]
        vmrs_b = all_vmrs[i + 1]
        if vmrs_a == vmrs_b:
            continue

        parts_a = vmrs_to_parts[vmrs_a]
        parts_b = vmrs_to_parts[vmrs_b]
        part_a, manuf_a = parts_a[0]
        part_b, manuf_b = parts_b[0]

        row_key = f"{part_a}|{manuf_a}+{part_b}|{manuf_b}"
        questions.append(
            TestQuestion(
                test_id=generate_test_id("comparison", row_key),
                category="comparison",
                expected_behavior="KNOWN_PRESENT",
                question_text=(
                    f"Do parts {part_a} and {part_b} have the same VMRS code?"
                ),
                row_key=row_key,
                expected_answer=f"{vmrs_a};{vmrs_b}",
                vendor_parts="",
            )
        )
        different_count += 1

    return questions


def write_output(questions: list[TestQuestion], output_path: Path) -> None:
    """Write questions to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "test_id",
        "category",
        "expected_behavior",
        "question_text",
        "row_key",
        "expected_answer",
        "vendor_parts",
        "pass_fail",
        "failure_type",
        "full_conversation",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for q in questions:
            writer.writerow(
                {
                    "test_id": q.test_id,
                    "category": q.category,
                    "expected_behavior": q.expected_behavior,
                    "question_text": q.question_text,
                    "row_key": q.row_key,
                    "expected_answer": q.expected_answer,
                    "vendor_parts": q.vendor_parts,
                    "pass_fail": "",
                    "failure_type": "",
                    "full_conversation": "",
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate test questions from vendor CSV with oracle data."
    )
    parser.add_argument(
        "--vendor-csv",
        type=Path,
        default=DEFAULT_VENDOR_CSV,
        help="Path to the vendor CSV file",
    )
    args = parser.parse_args()

    # Resolve paths relative to project root
    project_root = Path(__file__).resolve().parent.parent.parent
    vendor_csv = project_root / args.vendor_csv
    output_path = project_root / OUTPUT_PATH

    print(f"Loading vendor data from: {vendor_csv}")
    rows = load_vendor_csv(vendor_csv)
    print(f"Loaded {len(rows)} valid rows")

    part_to_vmrs, vmrs_to_parts = build_indexes(rows)
    print(f"Found {len(part_to_vmrs)} unique parts")
    print(f"Found {len(vmrs_to_parts)} unique VMRS codes")

    rng = random.Random(SEED)

    all_questions: list[TestQuestion] = []

    print("\nGenerating questions by category:")

    questions = generate_part_lookup(rows, part_to_vmrs, rng)
    print(f"  part_lookup: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_vendor_lookup(rows, rng)
    print(f"  vendor_lookup: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_description_exact(rows, rng)
    print(f"  description_exact: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_description_partial(rows, rng)
    print(f"  description_partial: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_hierarchy_navigation(rows, rng)
    print(f"  hierarchy_navigation: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_vendor_mapping(rows, vmrs_to_parts, rng)
    print(f"  vendor_mapping: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_validation_valid(rows, rng)
    print(f"  validation_valid: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_validation_invalid(rows, rng)
    print(f"  validation_invalid: {len(questions)}")
    all_questions.extend(questions)

    questions = generate_comparison(rows, vmrs_to_parts, rng)
    print(f"  comparison: {len(questions)}")
    all_questions.extend(questions)

    print(f"\nTotal questions: {len(all_questions)}")

    write_output(all_questions, output_path)
    print(f"\nWrote output to: {output_path}")


if __name__ == "__main__":
    main()
