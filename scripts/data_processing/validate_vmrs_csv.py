#!/usr/bin/env python3
import csv
import json
import os
import re
from html import unescape

ROOT = "/Users/thuptenwangpo/Documents/GitHub/vrms"
IN_DIR = os.path.join(ROOT, "md data")
CSV_DIR = os.path.join(ROOT, "csv data")
REPORT_PATH = os.path.join(CSV_DIR, "validation_report.json")

RE_HTML = re.compile(r"<[^>]+>")
RE_CODE9_ANYWHERE = re.compile(r"(\d{3})\s*[- ]\s*(\d{3})\s*[- ]\s*(\d{3})")
RE_CODE6_ANYWHERE = re.compile(r"(\d{3})\s*[- ]\s*(\d{3})")
RE_3D = re.compile(r"^\s*(\d{3})\s*$")
RE_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def strip_html(text: str) -> str:
    return RE_HTML.sub("", unescape(text or "")).strip()


def normalize_3group(a: str, b: str, c: str) -> str:
    return f"{int(a):03d}-{int(b):03d}-{int(c):03d}"


def normalize_2group(a: str, b: str) -> str:
    return f"{int(a):03d}-{int(b):03d}"


def is_pipe_line(line: str) -> bool:
    return line.count("|") >= 2


def split_pipe_row(line: str):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def parse_pipe_table(block_lines):
    rows = []
    for ln in block_lines:
        if not is_pipe_line(ln):
            continue
        if RE_TABLE_SEP.match(ln.strip()):
            continue
        parts = split_pipe_row(ln)
        if not parts:
            continue
        if all(p == "" for p in parts):
            continue
        rows.append(parts)
    return rows


def has_header_row(first_row):
    lower = [p.lower() for p in first_row]
    header_tokens = {"code", "description", "system", "subcode"}
    return any(token in header_tokens for token in lower)


def parse_md_codes(md_path: str):
    with open(md_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    codes = set()
    i = 0
    n = len(lines)
    while i < n:
        if is_pipe_line(lines[i]):
            j = i
            block = []
            while j < n and is_pipe_line(lines[j]):
                block.append(lines[j].rstrip('\n'))
                j += 1
            rows = parse_pipe_table(block)
            if rows:
                data_start_idx = 1 if has_header_row(rows[0]) else 0
                data_rows = rows[data_start_idx:]
                for r in data_rows:
                    cells = [strip_html(c) for c in r]
                    # scan multi-pair patterns per row
                    c = 0
                    L = len(cells)
                    while c < L:
                        a = cells[c]
                        mA = RE_3D.match(a)
                        mB = None
                        if mA and c + 1 < L:
                            mB = RE_3D.match(cells[c + 1])
                        if mA and mB:
                            codes.add(("6", normalize_2group(mA.group(1), mB.group(1))))
                            c += 3
                            continue
                        m9 = RE_CODE9_ANYWHERE.search(a)
                        if m9:
                            codes.add(("9", normalize_3group(*m9.groups())))
                            c += 2
                            continue
                        m6 = RE_CODE6_ANYWHERE.search(a)
                        if m6:
                            codes.add(("6", normalize_2group(*m6.groups())))
                            c += 2
                            continue
                        c += 1
            i = j
            continue
        i += 1
    return codes


def parse_csv_codes(csv_path: str):
    codes = set()
    if not os.path.exists(csv_path):
        return codes
    with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c9 = (row.get('code_9d') or '').strip()
            c6 = (row.get('code_6d') or '').strip()
            if c9:
                codes.add(("9", c9))
            if c6:
                codes.add(("6", c6))
    return codes


def main():
    md_files = [f for f in os.listdir(IN_DIR) if f.lower().endswith('.md')]
    md_files.sort()

    report = {"files": [], "totals": {"md_codes": 0, "csv_codes": 0, "md_only": 0, "csv_only": 0}}

    for md_name in md_files:
        md_path = os.path.join(IN_DIR, md_name)
        csv_name = os.path.splitext(md_name)[0] + ".csv"
        csv_path = os.path.join(CSV_DIR, csv_name)

        md_codes = parse_md_codes(md_path)
        csv_codes = parse_csv_codes(csv_path)

        md_only = sorted(md_codes - csv_codes)[:25]
        csv_only = sorted(csv_codes - md_codes)[:25]

        report["files"].append({
            "file": md_name,
            "md_codes": len(md_codes),
            "csv_codes": len(csv_codes),
            "md_only_count": len(md_codes - csv_codes),
            "csv_only_count": len(csv_codes - md_codes),
            "md_only_samples": md_only,
            "csv_only_samples": csv_only,
        })
        report["totals"]["md_codes"] += len(md_codes)
        report["totals"]["csv_codes"] += len(csv_codes)
        report["totals"]["md_only"] += len(md_codes - csv_codes)
        report["totals"]["csv_only"] += len(csv_codes - md_codes)

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps(report["totals"], indent=2))


if __name__ == '__main__':
    main()
