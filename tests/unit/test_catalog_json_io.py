"""Tests for validated catalog JSON file input."""

import json
from pathlib import Path
from typing import TextIO

import pytest

from opspilot.catalog import (
    CatalogFileReadError,
    CatalogJsonError,
    CatalogStructureError,
    load_catalog_records,
)

VALID_RECORD = {
    "id": "prod-001",
    "name": "API Monitoring",
    "category": "observability",
    "price": 49.99,
    "active": True,
    "tags": ["monitoring", "api"],
}


def test_load_valid_json_records(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps([VALID_RECORD]), encoding="utf-8")

    assert load_catalog_records(catalog_path) == [VALID_RECORD]


def test_load_empty_catalog(tmp_path: Path) -> None:
    catalog_path = tmp_path / "empty.json"
    catalog_path.write_text("[]", encoding="utf-8")

    assert load_catalog_records(catalog_path) == []


def test_optional_tags_default_is_preserved(tmp_path: Path) -> None:
    record = {key: value for key, value in VALID_RECORD.items() if key != "tags"}
    catalog_path = tmp_path / "without-tags.json"
    catalog_path.write_text(json.dumps([record]), encoding="utf-8")

    loaded = load_catalog_records(catalog_path)

    assert loaded[0].get("tags", []) == []


def test_extra_fields_are_preserved(tmp_path: Path) -> None:
    record = {**VALID_RECORD, "source": "seed-data"}
    catalog_path = tmp_path / "extra-field.json"
    catalog_path.write_text(json.dumps([record]), encoding="utf-8")

    assert load_catalog_records(catalog_path)[0]["source"] == "seed-data"


@pytest.mark.parametrize("payload", ["{}", "null", "42", '"records"'])
def test_reject_non_array_root(tmp_path: Path, payload: str) -> None:
    catalog_path = tmp_path / "wrong-root.json"
    catalog_path.write_text(payload, encoding="utf-8")

    with pytest.raises(CatalogStructureError, match="Expected a JSON array"):
        load_catalog_records(catalog_path)


def test_reject_non_object_record(tmp_path: Path) -> None:
    catalog_path = tmp_path / "non-object-record.json"
    catalog_path.write_text("[null]", encoding="utf-8")

    with pytest.raises(CatalogStructureError, match="record 0"):
        load_catalog_records(catalog_path)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"id": None}, "id.*non-empty string"),
        ({"name": " "}, "name.*non-empty string"),
        ({"category": 2}, "category.*non-empty string"),
        ({"price": True}, "price.*number"),
        ({"price": "12.50"}, "price.*number"),
        ({"price": 1e309}, "price.*finite"),
        ({"active": 1}, "active.*boolean"),
        ({"tags": "api"}, "tags.*array of strings"),
        ({"tags": ["api", 4]}, "tags.*array of strings"),
    ],
)
def test_reject_invalid_record_fields(
    tmp_path: Path, changes: dict[str, object], message: str
) -> None:
    catalog_path = tmp_path / "invalid-record.json"
    record = {**VALID_RECORD, **changes}
    catalog_path.write_text(json.dumps([record]), encoding="utf-8")

    with pytest.raises(CatalogStructureError, match=message):
        load_catalog_records(catalog_path)


def test_reject_missing_required_field(tmp_path: Path) -> None:
    catalog_path = tmp_path / "missing-field.json"
    record = {key: value for key, value in VALID_RECORD.items() if key != "active"}
    catalog_path.write_text(json.dumps([record]), encoding="utf-8")

    with pytest.raises(CatalogStructureError, match="Missing required field 'active'"):
        load_catalog_records(catalog_path)


def test_missing_file_is_wrapped_and_chained(tmp_path: Path) -> None:
    catalog_path = tmp_path / "missing.json"

    with pytest.raises(CatalogFileReadError, match="Could not read") as error:
        load_catalog_records(catalog_path)

    assert isinstance(error.value.__cause__, FileNotFoundError)


def test_unreadable_file_is_wrapped_and_chained(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_open(
        self: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> TextIO:
        if self.name == "unreadable.json":
            raise PermissionError("permission denied")
        raise AssertionError(f"Unexpected file opened by test double: {self}")

    monkeypatch.setattr(Path, "open", fail_open)

    with pytest.raises(CatalogFileReadError, match="permission denied") as error:
        load_catalog_records(Path("unreadable.json"))

    assert isinstance(error.value.__cause__, PermissionError)


def test_malformed_json_is_wrapped_and_chained(tmp_path: Path) -> None:
    catalog_path = tmp_path / "malformed.json"
    catalog_path.write_text("[{invalid]", encoding="utf-8")

    with pytest.raises(CatalogJsonError, match="line 1, column") as error:
        load_catalog_records(catalog_path)

    assert isinstance(error.value.__cause__, json.JSONDecodeError)


def test_invalid_utf8_is_wrapped_and_chained(tmp_path: Path) -> None:
    catalog_path = tmp_path / "invalid-encoding.json"
    catalog_path.write_bytes(b"[\xff]")

    with pytest.raises(CatalogFileReadError, match="not valid UTF-8") as error:
        load_catalog_records(catalog_path)

    assert isinstance(error.value.__cause__, UnicodeDecodeError)
