from __future__ import annotations

import pytest

from commitlint_local.cli import (
    ValidationError,
    main,
    parse_commit_message,
    validate_commit_message,
)

POSITIVE_MESSAGE = "feat(api): add missing response"
NEGATIVE_MESSAGE = "this is definitely invalid"
EDGE_EMPTY_MESSAGE = ""
EDGE_SCOPE_MIXED_CASE = "fix(APi): scope must be lowercase"
EDGE_WITH_FOOTER = "feat(ui): dark mode\n\nBREAKING CHANGE: updated theme tokens"


def test_parse_commit_message_valid() -> None:
    parsed = parse_commit_message("feat(repo): add help output")
    assert parsed["type"] == "feat"
    assert parsed["scope"] == "repo"
    assert parsed["description"] == "add help output"


def test_parse_commit_message_no_colon_raises() -> None:
    with pytest.raises(ValidationError):
        parse_commit_message("no colon here")


def test_validate_positive_commit() -> None:
    valid, meta = validate_commit_message(POSITIVE_MESSAGE)
    assert valid is True


def test_validate_negative_commit() -> None:
    with pytest.raises(ValidationError):
        validate_commit_message(NEGATIVE_MESSAGE)


def test_validate_edge_empty() -> None:
    valid, meta = validate_commit_message(EDGE_EMPTY_MESSAGE)
    assert valid is False
    assert meta == "commit message must not be empty"


def test_validate_edge_scope_mixed_case() -> None:
    valid, meta = validate_commit_message(EDGE_SCOPE_MIXED_CASE)
    assert valid is False
    assert "lowercase" in meta


def test_main_validates_and_returns_zero() -> None:
    rc = main(["validate", POSITIVE_MESSAGE])
    assert rc == 0


def test_main_returns_one_for_invalid_message() -> None:
    rc = main(["validate", NEGATIVE_MESSAGE])
    assert rc == 1


def test_main_returns_one_when_no_message() -> None:
    rc = main(["validate"])
    assert rc == 1


def test_main_list_types() -> None:
    rc = main(["list-types"])
    assert rc == 0
