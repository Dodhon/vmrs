"""
Stress Test MCP Server
Provides read/write access to manual_test_results.csv for Claude Desktop
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("stress-test")

# Path to the CSV file
CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "tests", "stress_test", "manual_test_results.csv"
)

def read_csv() -> List[Dict[str, str]]:
    """Read all rows from the CSV file."""
    with open(CSV_PATH, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(rows: List[Dict[str, str]]) -> None:
    """Write all rows to the CSV file."""
    if not rows:
        return
    fieldnames = rows[0].keys()
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

@mcp.tool()
async def get_next_test() -> Dict[str, Any]:
    """
    Get the next untested question from the stress test spreadsheet.

    Returns the first test case with pass_fail = 'NOT_TESTED'.
    """
    rows = read_csv()
    for row in rows:
        if row.get('pass_fail') == 'NOT_TESTED':
            return {
                "status": "found",
                "test": {
                    "id": row['id'],
                    "category": row['category'],
                    "subcategory": row['subcategory'],
                    "question": row['question'],
                    "expected_vmrs": row['expected_vmrs'],
                    "expected_behavior": row['expected_behavior']
                }
            }
    return {"status": "complete", "message": "All tests have been completed!"}

@mcp.tool()
async def get_test_by_id(test_id: str) -> Dict[str, Any]:
    """
    Get a specific test case by its ID.

    Args:
        test_id: The test ID (e.g., 'DQ-001', 'AM-005')
    """
    rows = read_csv()
    for row in rows:
        if row['id'] == test_id:
            return {
                "status": "found",
                "test": row
            }
    return {"status": "not_found", "message": f"Test ID '{test_id}' not found"}

@mcp.tool()
async def record_result(
    test_id: str,
    actual_response: str,
    pass_fail: str,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Record the result of a test case.

    Args:
        test_id: The test ID (e.g., 'DQ-001')
        actual_response: The actual chatbot response
        pass_fail: Result - must be one of: PASS, FAIL, PARTIAL, NOT_TESTED
        notes: Optional notes about the test
    """
    valid_results = ['PASS', 'FAIL', 'PARTIAL', 'NOT_TESTED']
    if pass_fail.upper() not in valid_results:
        return {
            "status": "error",
            "message": f"Invalid pass_fail value. Must be one of: {valid_results}"
        }

    rows = read_csv()
    updated = False
    for row in rows:
        if row['id'] == test_id:
            row['actual_response'] = actual_response
            row['pass_fail'] = pass_fail.upper()
            row['notes'] = notes
            row['tested_at'] = datetime.now().isoformat()
            updated = True
            break

    if not updated:
        return {"status": "error", "message": f"Test ID '{test_id}' not found"}

    write_csv(rows)
    return {
        "status": "success",
        "message": f"Recorded result for {test_id}: {pass_fail.upper()}"
    }

@mcp.tool()
async def get_test_stats() -> Dict[str, Any]:
    """
    Get statistics about test progress.

    Returns counts by pass/fail status and by category.
    """
    rows = read_csv()

    # Count by status
    status_counts = {
        'PASS': 0,
        'FAIL': 0,
        'PARTIAL': 0,
        'NOT_TESTED': 0
    }

    # Count by category
    category_counts = {}
    category_pass_counts = {}

    for row in rows:
        status = row.get('pass_fail', 'NOT_TESTED')
        if status in status_counts:
            status_counts[status] += 1

        category = row.get('category', 'unknown')
        if category not in category_counts:
            category_counts[category] = 0
            category_pass_counts[category] = 0
        category_counts[category] += 1
        if status == 'PASS':
            category_pass_counts[category] += 1

    total = len(rows)
    tested = total - status_counts['NOT_TESTED']

    return {
        "total_tests": total,
        "tested": tested,
        "remaining": status_counts['NOT_TESTED'],
        "status_counts": status_counts,
        "pass_rate": f"{(status_counts['PASS'] / tested * 100):.1f}%" if tested > 0 else "N/A",
        "by_category": {
            cat: {
                "total": category_counts[cat],
                "passed": category_pass_counts[cat]
            }
            for cat in category_counts
        }
    }

@mcp.tool()
async def list_tests(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    List test cases with optional filtering.

    Args:
        category: Filter by category (e.g., 'data_quality', 'ambiguity')
        status: Filter by status (e.g., 'NOT_TESTED', 'PASS', 'FAIL')
        limit: Maximum number of results to return (default 10)
    """
    rows = read_csv()
    filtered = []

    for row in rows:
        if category and row.get('category') != category:
            continue
        if status and row.get('pass_fail') != status.upper():
            continue
        filtered.append({
            'id': row['id'],
            'category': row['category'],
            'question': row['question'][:80] + '...' if len(row['question']) > 80 else row['question'],
            'pass_fail': row['pass_fail']
        })
        if len(filtered) >= limit:
            break

    return {
        "count": len(filtered),
        "total_matching": sum(1 for r in rows if
            (not category or r.get('category') == category) and
            (not status or r.get('pass_fail') == status.upper())
        ),
        "tests": filtered
    }

@mcp.tool()
async def get_categories() -> Dict[str, Any]:
    """
    Get list of all test categories and their counts.
    """
    rows = read_csv()
    categories = {}
    for row in rows:
        cat = row.get('category', 'unknown')
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in sorted(categories.items())
        ]
    }

if __name__ == "__main__":
    print(f"Starting Stress Test MCP Server...")
    print(f"CSV Path: {CSV_PATH}")
    print("Tools available: get_next_test, get_test_by_id, record_result, get_test_stats, list_tests, get_categories")
    mcp.run()
