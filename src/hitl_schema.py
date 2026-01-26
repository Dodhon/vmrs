"""Canonical HITL (Human-in-the-loop) submission/review schema.

This module is the single source of truth for:
- schema version stamping
- validation helpers used by MCP servers
- a prompt-safe schema excerpt (deterministic)

Keep this module dependency-free (stdlib only).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION: int = 2


VALID_SUBMISSION_TYPES = ("correction", "addition", "context", "question")
VALID_REVIEW_OUTCOMES = ("approved", "rejected")


@dataclass(frozen=True)
class ValidationErrorDetail:
    field: str
    message: str


def _is_nonempty_str(val: Any) -> bool:
    return isinstance(val, str) and bool(val.strip())


def _optional_nonempty_str(field_name: str, val: Any) -> Optional[ValidationErrorDetail]:
    if val is None:
        return None
    if not _is_nonempty_str(val):
        return ValidationErrorDetail(field_name, "must be a non-empty string when provided")
    return None


def validate_pending_submission_input(
    *,
    type: Any,
    description: Any,
    vmrs_code: Any,
    context: Any,
    related_query: Any,
    submitter: Any,
    target_type: Any = None,
    target_key: Any = None,
    context_pack: Any = None,
    targets: Any = None,
    proposed_action: Any = None,
    proposed_payload: Any = None,
) -> List[ValidationErrorDetail]:
    """Validate the input args to the Step 1 MCP tool submit_knowledge().

    Returns:
        A list of validation errors (empty if valid).

    Notes:
        This validates the *tool inputs*, not the written JSON.
    """

    errors: List[ValidationErrorDetail] = []

    if type not in VALID_SUBMISSION_TYPES:
        errors.append(
            ValidationErrorDetail(
                "type",
                f"Invalid type. Must be one of: {sorted(VALID_SUBMISSION_TYPES)}",
            )
        )

    if not _is_nonempty_str(description):
        errors.append(ValidationErrorDetail("description", "is required"))

    # Step 3 workflow required fields
    if not _is_nonempty_str(vmrs_code):
        errors.append(ValidationErrorDetail("vmrs_code", "is required"))
    if not _is_nonempty_str(context):
        errors.append(ValidationErrorDetail("context", "is required"))
    if not _is_nonempty_str(related_query):
        errors.append(ValidationErrorDetail("related_query", "is required"))

    if not isinstance(submitter, dict):
        errors.append(ValidationErrorDetail("submitter", "is required and must be an object"))
    else:
        if not _is_nonempty_str(submitter.get("name")):
            errors.append(ValidationErrorDetail("submitter.name", "is required"))
        if not _is_nonempty_str(submitter.get("role")):
            errors.append(ValidationErrorDetail("submitter.role", "is required"))

    if target_type is not None and not isinstance(target_type, str):
        errors.append(ValidationErrorDetail("target_type", "must be a string when provided"))
    if target_key is not None and not isinstance(target_key, dict):
        errors.append(ValidationErrorDetail("target_key", "must be an object when provided"))

    if context_pack is not None and not isinstance(context_pack, dict):
        errors.append(ValidationErrorDetail("context_pack", "must be an object when provided"))
    if isinstance(context_pack, dict):
        excerpt = context_pack.get("answer_excerpt_or_summary")
        if isinstance(excerpt, str) and len(excerpt) > 500:
            errors.append(
                ValidationErrorDetail(
                    "context_pack.answer_excerpt_or_summary",
                    "must be <= 500 characters; please shorten it",
                )
            )

    if targets is not None and not isinstance(targets, list):
        errors.append(ValidationErrorDetail("targets", "must be a list when provided"))
    if isinstance(targets, list):
        if len(targets) == 0:
            errors.append(ValidationErrorDetail("targets", "must be a non-empty list when provided"))
        else:
            first = targets[0]
            if not isinstance(first, dict):
                errors.append(
                    ValidationErrorDetail(
                        "targets[0]",
                        "must be an object with target_type and target_key",
                    )
                )
            else:
                if "target_type" not in first or "target_key" not in first:
                    errors.append(
                        ValidationErrorDetail(
                            "targets[0]",
                            "must include target_type and target_key",
                        )
                    )

    if proposed_action is not None and not isinstance(proposed_action, str):
        errors.append(ValidationErrorDetail("proposed_action", "must be a string when provided"))
    if proposed_payload is not None and not isinstance(proposed_payload, dict):
        errors.append(ValidationErrorDetail("proposed_payload", "must be an object when provided"))

    return errors


def validate_review_input(
    *,
    submission_id: Any,
    outcome: Any,
    reviewed_by: Any,
    review_notes: Any,
    operator_name: Any,
    operator_role: Any,
    operator_id: Any = None,
    operator_team: Any = None,
) -> List[ValidationErrorDetail]:
    """Validate the input args to the Step 2 MCP tool record_review()."""

    errors: List[ValidationErrorDetail] = []

    if not _is_nonempty_str(submission_id):
        errors.append(ValidationErrorDetail("submission_id", "is required"))

    if outcome not in VALID_REVIEW_OUTCOMES:
        errors.append(ValidationErrorDetail("outcome", "must be 'approved' or 'rejected'"))

    if not _is_nonempty_str(reviewed_by):
        errors.append(ValidationErrorDetail("reviewed_by", "is required"))
    if not _is_nonempty_str(review_notes):
        errors.append(ValidationErrorDetail("review_notes", "is required"))

    if not _is_nonempty_str(operator_name):
        errors.append(ValidationErrorDetail("operator_name", "is required"))
    if not _is_nonempty_str(operator_role):
        errors.append(ValidationErrorDetail("operator_role", "is required"))

    for name, val in ("operator_id", operator_id), ("operator_team", operator_team):
        maybe = _optional_nonempty_str(name, val)
        if maybe:
            errors.append(maybe)

    return errors


def _schema_lines() -> List[str]:
    """Deterministic, prompt-safe schema excerpt lines."""

    # Keep this very compact; prompts should not embed walls of JSON schema.
    return [
        "HITL JSON schema (canonical excerpt)",
        f"schema_version: int = {SCHEMA_VERSION}",
        "",
        "Pending submission JSON (HitL_local/pending/<id>.json):",
        "  Top-level:",
        "    schema_version: int",
        "    id: str  (e.g., 'HITL-<uuid>')",
        "    type: 'correction'|'addition'|'context'|'question'",
        "    submitted_at_ms: int",
        "    status: 'pending'",
        "    submitter: {name: str, role: str, ...}",
        "    content: { ... }",
        "  content (required):",
        "    vmrs_code: str",
        "    description: str",
        "    context: str",
        "    related_query: str",
        "  content (optional):",
        "    target_type: str",
        "    target_key: object",
        "    targets: list[object]  (if provided, non-empty; targets[0] has target_type+target_key)",
        "    context_pack: object  (answer_excerpt_or_summary <= 500 chars)",
        "    proposed_action: str",
        "    proposed_payload: object",
        "",
        "Reviewed submission JSON (HitL_local/reviewed/{approved|rejected}/<id>.json):",
        "  status: 'reviewed'",
        "  review: {",
        "    decision: 'approved'|'rejected',",
        "    reviewed_at_ms: int,",
        "    notes: str,",
        "    operator: {name: str, role: str, id?: str, team?: str}",
        "  }",
        "  Legacy mirrors (for back-compat): decision, reviewed_at_ms, review_notes, reviewed_by",
    ]


def render_prompt_schema_excerpt() -> str:
    """Render the canonical prompt excerpt as a single string."""

    return "\n".join(_schema_lines()).rstrip() + "\n"


def write_prompt_schema_excerpt(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_prompt_schema_excerpt(), encoding="utf-8")


def check_prompt_schema_excerpt(path: Path) -> Tuple[bool, str]:
    expected = render_prompt_schema_excerpt()
    try:
        actual = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False, f"Missing excerpt file: {path}"

    if actual != expected:
        return False, f"Excerpt file is stale: {path} (run --write-excerpt)"
    return True, "OK"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HITL schema helpers")
    parser.add_argument("--write-excerpt", type=str, default=None, help="Write prompt excerpt to this path")
    parser.add_argument("--check-excerpt", type=str, default=None, help="Check prompt excerpt matches canonical")

    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.write_excerpt and not args.check_excerpt:
        parser.print_help()
        return 2

    if args.write_excerpt:
        write_prompt_schema_excerpt(Path(args.write_excerpt))

    if args.check_excerpt:
        ok, msg = check_prompt_schema_excerpt(Path(args.check_excerpt))
        if not ok:
            raise SystemExit(msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
