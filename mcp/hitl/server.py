"""
HITL Feedback Capture MCP Server (MVP)

Implements a file-first submission workflow:
- submit_knowledge -> writes JSON to HitL_local/pending/<id>.json
- get_submission_status -> checks pending submissions by ID
- list_submissions -> lists recent pending submissions
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hitl")


def _repo_root() -> Path:
    # server.py -> mcp/hitl/server.py; root is three parents up
    return Path(__file__).resolve().parents[2]


ROOT_DIR = _repo_root()
HITL_DIR = ROOT_DIR / "HitL_local"
PENDING_DIR = HITL_DIR / "pending"


def _ensure_dirs() -> None:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id() -> str:
    return f"HITL-{uuid.uuid4()}"


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_submission(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_pending_submission_path(submission_id: str) -> Optional[Path]:
    # MVP is pending-only. Reviewed handling comes later.
    candidate = PENDING_DIR / f"{submission_id}.json"
    return candidate if candidate.exists() else None


def _summarize_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    content = data.get("content") or {}
    desc = content.get("description")
    if isinstance(desc, str) and len(desc) > 120:
        desc = desc[:117] + "..."

    return {
        "id": data.get("id"),
        "type": data.get("type"),
        "status": data.get("status"),
        "submitted_at_ms": data.get("submitted_at_ms"),
        "vmrs_code": content.get("vmrs_code"),
        "description": desc,
    }


@mcp.tool()
async def submit_knowledge(
    type: str,
    description: str,
    vmrs_code: Optional[str] = None,
    context: Optional[str] = None,
    related_query: Optional[str] = None,
    target_type: Optional[str] = None,
    target_key: Optional[Dict[str, Any]] = None,
    proposed_action: Optional[str] = None,
    proposed_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new HITL submission and store it locally.

    Args:
        type: One of: correction|addition|context|question
        description: What the user wants to record (required)
        vmrs_code: Optional VMRS code (e.g. "047-000-000")
        context: Optional rationale / why valuable
        related_query: Optional query that prompted this
        target_type: Optional "Component"|"VendorPart"|...
        target_key: Optional stable identifier dict (e.g. {"code": "047-000-000"})
        proposed_action: Optional change intent (e.g. "set_property")
        proposed_payload: Optional change payload dict
    """
    _ensure_dirs()

    valid_types = {"correction", "addition", "context", "question"}
    if type not in valid_types:
        return {
            "status": "error",
            "message": f"Invalid type. Must be one of: {sorted(valid_types)}",
        }
    if not description or not isinstance(description, str):
        return {"status": "error", "message": "description is required"}

    submission_id = _new_id()
    data: Dict[str, Any] = {
        "id": submission_id,
        "type": type,
        "submitted_at_ms": _now_ms(),
        "status": "pending",
        "content": {
            "vmrs_code": vmrs_code,
            "description": description,
            "context": context,
            "related_query": related_query,
            "target_type": target_type,
            "target_key": target_key,
            "proposed_action": proposed_action,
            "proposed_payload": proposed_payload,
        },
    }

    # Strip null-ish keys inside content for smaller files
    data["content"] = {k: v for k, v in data["content"].items() if v is not None}

    out_path = PENDING_DIR / f"{submission_id}.json"
    _write_json(out_path, data)

    return {
        "status": "success",
        "id": submission_id,
        "path": str(out_path),
        "submission": _summarize_submission(data),
    }


@mcp.tool()
async def get_submission_status(submission_id: str) -> Dict[str, Any]:
    """
    Check submission status by ID (pending-only MVP).
    """
    _ensure_dirs()
    if not submission_id:
        return {"status": "error", "message": "submission_id is required"}

    path = _find_pending_submission_path(submission_id)
    if not path:
        return {"status": "not_found", "id": submission_id}

    data = _load_submission(path)
    return {
        "status": "found",
        "id": submission_id,
        "location": "pending",
        "submission": _summarize_submission(data),
    }


@mcp.tool()
async def list_submissions(limit: int = 10) -> Dict[str, Any]:
    """
    List recent pending submissions (pending-only MVP).

    Args:
        limit: Max number to return (default 10)
    """
    _ensure_dirs()
    paths = sorted(PENDING_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    submissions: List[Dict[str, Any]] = []
    for p in paths[: max(0, limit)]:
        try:
            submissions.append(_summarize_submission(_load_submission(p)))
        except Exception:
            submissions.append({"id": p.stem, "status": "error", "message": "Failed to read JSON"})

    return {
        "status": "success",
        "count": len(submissions),
        "submissions": submissions,
    }


if __name__ == "__main__":
    print("Starting HITL MCP Server...")
    print(f"Repo root: {ROOT_DIR}")
    print(f"HitL_local: {HITL_DIR}")
    print("Tools available: submit_knowledge, get_submission_status, list_submissions")
    mcp.run()

