"""Tests for the catalog processing command-line interface."""

import json
from pathlib import Path

import pytest

from scripts.process_catalog import main

VALID_RECORD = {
    "id": "prod-001",
    "name": "API Monitoring",
    "category": "observability",
    "price": 49.99,
    "active": True,
    "tags": ["monitoring", "api"],
}


def test_cli_success_prints_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps([VALID_RECORD]), encoding="utf-8")

    exit_code = main([str(catalog_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Total products: 1" in captured.out
    assert "API Monitoring" in captured.out
    assert captured.err == ""


def test_cli_file_error_is_clear_and_returns_error_code(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = main([str(tmp_path / "missing.json")])

    assert exit_code == 2
    assert "Catalog processing failed" in caplog.text
    assert "Could not read catalog file" in caplog.text
