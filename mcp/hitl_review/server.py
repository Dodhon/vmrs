"""
HITL Operator Review MCP Server (Step 2 MVP)

Implements a file-first review workflow over HITL submissions created by Step 1:
- list_submissions -> lists pending (and optionally reviewed) submissions
- get_submission -> fetches full pending submission JSON by id
- record_review -> validates + records an approved|rejected decision and moves the file
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hitl_review")


def _repo_root() -> Path:
    # server.py -> mcp/hitl_review/server.py; root is three parents up
    return Path(__file__).resolve().parents[2]


ROOT_DIR = _repo_root()
HITL_DIR = ROOT_DIR / "HitL_local"

PENDING_DIR = HITL_DIR / "pending"
REVIEWED_DIR = HITL_DIR / "reviewed"
APPROVED_DIR = REVIEWED_DIR / "approved"
REJECTED_DIR = REVIEWED_DIR / "rejected"


def _ensure_dirs() -> None:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _load_submission(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    tmp_path = path.with_name(f"{path.name}.tmp-{uuid.uuid4()}")
    tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _summarize_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    content = data.get("content") or {}
    desc = content.get("description")
    if isinstance(desc, str) and len(desc) > 120:
        desc = desc[:117] + "..."

    out: Dict[str, Any] = {
        "id": data.get("id"),
        "type": data.get("type"),
        "status": data.get("status"),
        "submitted_at_ms": data.get("submitted_at_ms"),
        "vmrs_code": content.get("vmrs_code"),
        "description": desc,
    }
    if "decision" in data:
        out["decision"] = data.get("decision")
    if "reviewed_at_ms" in data:
        out["reviewed_at_ms"] = data.get("reviewed_at_ms")
    return out


def _dir_for_location(location: str) -> Optional[Path]:
    if location == "pending":
        return PENDING_DIR
    if location == "approved":
        return APPROVED_DIR
    if location == "rejected":
        return REJECTED_DIR
    return None


def _validate_id_matches_filename(path: Path, data: Dict[str, Any]) -> Optional[str]:
    submission_id = data.get("id")
    if not isinstance(submission_id, str) or not submission_id:
        return "Missing or invalid 'id' field"
    if path.stem != submission_id:
        return f"Filename/id mismatch: filename '{path.stem}' != id '{submission_id}'"
    return None


@mcp.tool()
async def list_submissions(limit: int = 10, location: str = "pending") -> Dict[str, Any]:
    """
    List recent HITL submissions from a location.

    Args:
        limit: Max number to return (default 10)
        location: One of: pending|approved|rejected (default pending)
    """
    _ensure_dirs()

    if limit < 0:
        return {"status": "error", "message": "limit must be >= 0"}

    base_dir = _dir_for_location(location)
    if not base_dir:
        return {
            "status": "error",
            "message": "Invalid location. Must be one of: pending, approved, rejected",
        }

    paths = sorted(base_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    submissions: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for p in paths[: max(0, limit)]:
        try:
            data = _load_submission(p)
        except Exception as e:
            errors.append({"id": p.stem, "status": "error", "message": f"Failed to read JSON: {e}"})
            continue

        mismatch = _validate_id_matches_filename(p, data)
        if mismatch:
            errors.append({"id": p.stem, "status": "error", "message": mismatch})
            continue

        if location == "pending" and data.get("status") != "pending":
            errors.append({"id": p.stem, "status": "error", "message": "Not pending; skipping"})
            continue

        submissions.append(_summarize_submission(data))

    return {
        "status": "success",
        "location": location,
        "count": len(submissions),
        "submissions": submissions,
        "errors": errors,
    }


@mcp.tool()
async def get_submission(submission_id: str) -> Dict[str, Any]:
    """
    Fetch a full pending submission by ID.
    """
    _ensure_dirs()
    if not submission_id:
        return {"status": "error", "message": "submission_id is required"}

    path = PENDING_DIR / f"{submission_id}.json"
    if not path.exists():
        return {"status": "not_found", "id": submission_id, "location": "pending"}

    try:
        data = _load_submission(path)
    except Exception as e:
        return {"status": "error", "message": f"Failed to read JSON: {e}"}

    mismatch = _validate_id_matches_filename(path, data)
    if mismatch:
        return {"status": "error", "message": mismatch}

    if data.get("status") != "pending":
        return {"status": "error", "message": "Only pending submissions can be fetched in Step 2"}

    return {"status": "success", "id": submission_id, "location": "pending", "submission": data}


@mcp.tool()
async def record_review(
    submission_id: str,
    outcome: str,
    reviewed_by: str,
    review_notes: str,
) -> Dict[str, Any]:
    """
    Record an operator review decision and move the submission out of pending.

    Validates:
    - pending/<id>.json exists
    - JSON id matches filename
    - status == "pending"
    - outcome is approved|rejected
    - review_notes is provided
    - reviewed_by is provided
    """
    _ensure_dirs()

    if not submission_id:
        return {"status": "error", "message": "submission_id is required"}
    if outcome not in {"approved", "rejected"}:
        return {"status": "error", "message": "outcome must be 'approved' or 'rejected'"}
    if not isinstance(reviewed_by, str) or not reviewed_by.strip():
        return {"status": "error", "message": "reviewed_by is required"}
    if not isinstance(review_notes, str) or not review_notes.strip():
        return {"status": "error", "message": "review_notes is required"}

    pending_path = PENDING_DIR / f"{submission_id}.json"
    if not pending_path.exists():
        return {"status": "not_found", "id": submission_id, "location": "pending"}

    try:
        data = _load_submission(pending_path)
    except Exception as e:
        return {"status": "error", "message": f"Failed to read JSON: {e}"}

    mismatch = _validate_id_matches_filename(pending_path, data)
    if mismatch:
        return {"status": "error", "message": mismatch}

    if data.get("status") != "pending":
        return {"status": "error", "message": "Only pending submissions can be reviewed"}

    dest_dir = APPROVED_DIR if outcome == "approved" else REJECTED_DIR
    dest_path = dest_dir / f"{submission_id}.json"
    if dest_path.exists():
        return {"status": "error", "message": "Reviewed destination already exists; refusing to overwrite"}

    staging_path = dest_dir / f"{submission_id}.json.staging-{uuid.uuid4()}"
    try:
        # Atomic move out of pending first (so we don't double-review)
        pending_path.replace(staging_path)
    except Exception as e:
        return {"status": "error", "message": f"Failed to move pending submission for review: {e}"}

    # Apply review metadata
    data["status"] = outcome
    data["decision"] = outcome
    data["reviewed_at_ms"] = _now_ms()
    data["reviewed_by"] = reviewed_by.strip()
    data["review_notes"] = review_notes.strip()

    try:
        # Atomic write into reviewed destination, then clean up staging
        _write_json_atomic(dest_path, data)
        if staging_path.exists():
            staging_path.unlink()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write reviewed submission (staging file may remain): {e}",
            "staging_path": str(staging_path),
        }

    return {
        "status": "success",
        "id": submission_id,
        "outcome": outcome,
        "path": str(dest_path),
        "submission": _summarize_submission(data),
    }


if __name__ == "__main__":
    print("Starting HITL Review MCP Server...")
    print(f"Repo root: {ROOT_DIR}")
    print(f"HitL_local: {HITL_DIR}")
    print("Tools available: list_submissions, get_submission, record_review")
    mcp.run()

