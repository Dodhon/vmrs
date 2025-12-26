#!/usr/bin/env python3
import csv
import json
import os
import re
import sys
from html import unescape

ROOT = "/Users/thuptenwangpo/Documents/GitHub/vmrs"
IN_DIR = os.path.join(ROOT, "md data")
OUT_DIR = os.path.join(ROOT, "csv data")
SUMMARY_PATH = os.path.join(OUT_DIR, "validation_summary.json")

RE_HTML = re.compile(r"<[^>]+>")
# Find codes anywhere in a text
RE_CODE9_ANYWHERE = re.compile(r"(\d{3})\s*[- ]\s*(\d{3})\s*[- ]\s*(\d{3})")
RE_CODE6_ANYWHERE = re.compile(r"(\d{3})\s*[- ]\s*(\d{3})")
# Plain 3-digit cell matcher
RE_3D = re.compile(r"^\s*(\d{3})\s*$")
# Markdown table alignment/separator like: | --- | :---: | --- |
RE_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def strip_html(text: str) -> str:
	return RE_HTML.sub("", unescape(text or "")).strip()


def normalize_3group(a: str, b: str, c: str) -> str:
	return f"{int(a):03d}-{int(b):03d}-{int(c):03d}"


def normalize_2group(a: str, b: str) -> str:
	return f"{int(a):03d}-{int(b):03d}"


def is_pipe_line(line: str) -> bool:
	# Detect lines that look like part of a markdown pipe table block
	return line.count("|") >= 2


def split_pipe_row(line: str):
	# split on '|' and strip, drop empties from edges
	parts = [c.strip() for c in line.strip().strip('|').split('|')]
	return parts


def parse_pipe_table(block_lines):
	rows = []
	for ln in block_lines:
		if not is_pipe_line(ln):
			continue
		if RE_TABLE_SEP.match(ln.strip()):
			# skip alignment/separator rows
			continue
		parts = split_pipe_row(ln)
		if not parts:
			continue
		# skip empty/spacer rows (e.g., '|' columns with blanks)
		if all(p == "" for p in parts):
			continue
		rows.append(parts)
	return rows


def has_header_row(first_row):
	lower = [p.lower() for p in first_row]
	header_tokens = {"code", "description", "system", "subcode"}
	return any(token in header_tokens for token in lower)


def write_csv_rows(path, fieldnames, rows):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, 'w', newline='', encoding='utf-8') as f:
		w = csv.DictWriter(f, fieldnames=fieldnames)
		w.writeheader()
		for r in rows:
			w.writerow(r)


def process_row_cells(cells, source_file, seen_codes, out_rows):
	"""Extract all code-description pairs from a table row.
	Handles multi-column layouts where rows contain multiple horizontal pairs.
	"""
	L = len(cells)
	
	# Detect and split multi-column layouts
	if L == 6:
		# Check if this is two 3-column groups: [sys, assy, desc, sys, assy, desc]
		if RE_3D.match(strip_html(cells[0])) and RE_3D.match(strip_html(cells[1])) and \
		   RE_3D.match(strip_html(cells[3])) and RE_3D.match(strip_html(cells[4])):
			process_single_group([cells[0], cells[1], cells[2]], source_file, seen_codes, out_rows)
			process_single_group([cells[3], cells[4], cells[5]], source_file, seen_codes, out_rows)
			return
	
	if L >= 4 and L % 2 == 0:
		# Check if this is pairs of [code, desc, code, desc, ...]
		all_even_are_codes = all(
			RE_CODE9_ANYWHERE.search(strip_html(cells[i])) or 
			RE_CODE6_ANYWHERE.search(strip_html(cells[i])) or 
			RE_3D.match(strip_html(cells[i]))
			for i in range(0, min(L, 4), 2) if i < L
		)
		if all_even_are_codes:
			for i in range(0, L, 2):
				if i + 1 < L:
					process_single_group([cells[i], cells[i+1]], source_file, seen_codes, out_rows)
			return
	
	# Fallback: process sequentially
	process_single_group(cells, source_file, seen_codes, out_rows)


def process_single_group(cells, source_file, seen_codes, out_rows):
	"""Process a single code-description group sequentially."""
	c = 0
	L = len(cells)
	while c < L:
		cell = strip_html(cells[c])
		
		# Check for 3-cell pattern: ddd | ddd | desc
		mA = RE_3D.match(cell)
		mB = None
		if mA and c + 1 < L:
			mB = RE_3D.match(strip_html(cells[c + 1]))
		if mA and mB:
			code_6d = normalize_2group(mA.group(1), mB.group(1))
			if ("6", code_6d) not in seen_codes:
				desc = strip_html(cells[c + 2]) if c + 2 < L else ""
				out_rows.append({
					"code_9d": "",
					"code_6d": code_6d,
					"system": f"{int(mA.group(1)):03d}",
					"subcode": f"{int(mB.group(1)):03d}",
					"description": desc,
					"source_file": source_file,
				})
				seen_codes.add(("6", code_6d))
			c += 3
			continue

		# Check for 9-digit code
		m9 = RE_CODE9_ANYWHERE.search(cell)
		if m9:
			code_9d = normalize_3group(*m9.groups())
			if ("9", code_9d) not in seen_codes:
				desc = strip_html(cells[c + 1]) if c + 1 < L else ""
				if c + 1 < L:
					next_cell = strip_html(cells[c + 1])
					if RE_CODE9_ANYWHERE.search(next_cell) or RE_CODE6_ANYWHERE.search(next_cell) or RE_3D.match(next_cell):
						desc = ""
				out_rows.append({
					"code_9d": code_9d,
					"code_6d": "",
					"system": f"{int(m9.group(1)):03d}",
					"subcode": f"{int(m9.group(2)):03d}",
					"description": desc,
					"source_file": source_file,
				})
				seen_codes.add(("9", code_9d))
			c += 2 if c + 1 < L else 1
			continue

		# Check for 6-digit code
		m6 = RE_CODE6_ANYWHERE.search(cell)
		if m6:
			code_6d = normalize_2group(*m6.groups())
			if ("6", code_6d) not in seen_codes:
				desc = strip_html(cells[c + 1]) if c + 1 < L else ""
				if c + 1 < L:
					next_cell = strip_html(cells[c + 1])
					if RE_CODE9_ANYWHERE.search(next_cell) or RE_CODE6_ANYWHERE.search(next_cell) or RE_3D.match(next_cell):
						desc = ""
				out_rows.append({
					"code_9d": "",
					"code_6d": code_6d,
					"system": f"{int(m6.group(1)):03d}",
					"subcode": f"{int(m6.group(2)):03d}",
					"description": desc,
					"source_file": source_file,
				})
				seen_codes.add(("6", code_6d))
			c += 2 if c + 1 < L else 1
			continue

		# No code found, advance
		c += 1


def process_file(in_path: str):
	source_file = os.path.basename(in_path)
	out_path = os.path.join(OUT_DIR, os.path.splitext(source_file)[0] + ".csv")

	with open(in_path, 'r', encoding='utf-8', errors='replace') as f:
		lines = f.readlines()

	# State for collecting outputs
	emitted = []
	seen_codes = set()  # dedupe per file on code only

	# Parse contiguous pipe table blocks only
	i = 0
	n = len(lines)
	while i < n:
		if is_pipe_line(lines[i]):
			j = i
			block = []
			while j < n and is_pipe_line(lines[j]):
				block.append(lines[j].rstrip('\n'))
				j += 1
			# try parse table
			rows = parse_pipe_table(block)
			if rows:
				# Determine if the first non-separator row is a header
				data_start_idx = 1 if has_header_row(rows[0]) else 0
				data_rows = rows[data_start_idx:]
				if not data_rows:
					i = j
					continue
				for r in data_rows:
					cells = [c.strip() for c in r]
					process_row_cells(cells, source_file, seen_codes, emitted)
			i = j
			continue
		i += 1

	# Decide columns (code-only rows; no generic columns)
	fieldnames = [
		"code_9d", "code_6d", "system", "subcode", "description", "source_file"
	]

	# Write CSV
	rows = []
	for r in emitted:
		row = {k: r.get(k, "") for k in fieldnames}
		rows.append(row)
	write_csv_rows(out_path, fieldnames, rows)

	# Basic validation stats
	stats = {
		"file": source_file,
		"rows": len(emitted),
		"rows_9d": 0,
		"rows_6d": 0,
		"invalid_9d": 0,
		"invalid_6d": 0,
	}
	for r in emitted:
		c9 = r.get("code_9d", "")
		c6 = r.get("code_6d", "")
		if c9:
			if re.fullmatch(r"\d{3}-\d{3}-\d{3}", c9):
				stats["rows_9d"] += 1
			else:
				stats["invalid_9d"] += 1
		if c6:
			if re.fullmatch(r"\d{3}-\d{3}", c6):
				stats["rows_6d"] += 1
			else:
				stats["invalid_6d"] += 1
	return stats


def main():
	if not os.path.isdir(IN_DIR):
		print(f"Input directory not found: {IN_DIR}", file=sys.stderr)
		sys.exit(1)
	os.makedirs(OUT_DIR, exist_ok=True)

	md_files = [
		os.path.join(IN_DIR, f) for f in os.listdir(IN_DIR)
		if f.lower().endswith('.md')
	]
	md_files.sort()

	summary = {
		"total_files": len(md_files),
		"files": [],
		"totals": {
			"rows": 0,
			"rows_9d": 0,
			"rows_6d": 0,
			"invalid_9d": 0,
			"invalid_6d": 0,
		}
	}

	for p in md_files:
		try:
			stats = process_file(p)
			summary["files"].append(stats)
			for k in summary["totals"].keys():
				summary["totals"][k] += stats.get(k, 0)
		except Exception as e:
			summary["files"].append({"file": os.path.basename(p), "error": str(e)})

	with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
		json.dump(summary, f, indent=2, ensure_ascii=False)

	print(json.dumps(summary["totals"], indent=2))


if __name__ == "__main__":
	main()
