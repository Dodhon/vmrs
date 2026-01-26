from __future__ import annotations

from pathlib import Path

import pytest

from src.hitl_schema import (
    SCHEMA_VERSION,
    check_prompt_schema_excerpt,
    render_prompt_schema_excerpt,
    validate_pending_submission_input,
    validate_review_input,
    write_prompt_schema_excerpt,
)


def test_validate_pending_submission_input_valid_minimal() -> None:
    errors = validate_pending_submission_input(
        type="correction",
        description="Fix description",
        vmrs_code="047-000-000",
        context="Evidence here",
        related_query="What is 047-000-000?",
        submitter={"name": "Alice", "role": "user"},
    )
    assert errors == []


@pytest.mark.parametrize(
    "field_overrides, expected_field",
    [
        ({"type": "bogus"}, "type"),
        ({"description": ""}, "description"),
        ({"vmrs_code": ""}, "vmrs_code"),
        ({"context": ""}, "context"),
        ({"related_query": ""}, "related_query"),
        ({"submitter": None}, "submitter"),
        ({"submitter": {}}, "submitter.name"),
        ({"submitter": {"name": "Alice"}}, "submitter.role"),
    ],
)
def test_validate_pending_submission_input_required_fields(field_overrides, expected_field) -> None:
    kwargs = dict(
        type="correction",
        description="Fix description",
        vmrs_code="047-000-000",
        context="Evidence here",
        related_query="What is 047-000-000?",
        submitter={"name": "Alice", "role": "user"},
    )
    kwargs.update(field_overrides)
    errors = validate_pending_submission_input(**kwargs)
    assert errors
    assert errors[0].field == expected_field


def test_validate_pending_submission_input_context_pack_excerpt_max_len() -> None:
    errors = validate_pending_submission_input(
        type="addition",
        description="Add note",
        vmrs_code="047-000-000",
        context="Evidence here",
        related_query="Q",
        submitter={"name": "Alice", "role": "user"},
        context_pack={"answer_excerpt_or_summary": "x" * 501},
    )
    assert errors
    assert errors[0].field == "context_pack.answer_excerpt_or_summary"


def test_validate_review_input_valid_minimal() -> None:
    errors = validate_review_input(
        submission_id="HITL-123",
        outcome="approved",
        reviewed_by="operator@example.com",
        review_notes="Looks good",
        operator_name="Bob",
        operator_role="reviewer",
    )
    assert errors == []


def test_validate_review_input_rejects_bad_outcome() -> None:
    errors = validate_review_input(
        submission_id="HITL-123",
        outcome="maybe",
        reviewed_by="x",
        review_notes="y",
        operator_name="Bob",
        operator_role="reviewer",
    )
    assert errors
    assert errors[0].field == "outcome"


def test_render_prompt_schema_excerpt_is_deterministic_and_mentions_version() -> None:
    a = render_prompt_schema_excerpt()
    b = render_prompt_schema_excerpt()
    assert a == b
    assert f"schema_version: int = {SCHEMA_VERSION}" in a


def test_excerpt_file_roundtrip_and_check(tmp_path: Path) -> None:
    p = tmp_path / "hitl_schema_excerpt.txt"
    write_prompt_schema_excerpt(p)
    ok, msg = check_prompt_schema_excerpt(p)
    assert ok, msg

    # Make it stale
    p.write_text(p.read_text(encoding="utf-8") + "\n# stale\n", encoding="utf-8")
    ok, msg = check_prompt_schema_excerpt(p)
    assert not ok
    assert "stale" in msg.lower()
