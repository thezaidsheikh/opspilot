"""Tests for robust JSONL log file processing."""

import json
from pathlib import Path

import pytest

from opspilot.ingestion import (
    LogFileError,
    LogFileReadError,
    LogLineError,
    LogRecord,
    iter_log_records,
    process_log_file,
)

VALID_LINES = [
    {"level": "INFO", "service": "payment-api", "message": "charge succeeded"},
    {"level": "ERROR", "service": "payment-api", "message": "charge failed"},
    {"level": "WARNING", "service": "auth", "message": "slow login"},
]


def _write_log(tmp_path: Path, name: str, lines: list[str]) -> Path:
    log_path = tmp_path / name
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_path


def _as_jsonl(records: list[dict[str, object]]) -> list[str]:
    return [json.dumps(record) for record in records]


def test_process_valid_lines(tmp_path: Path) -> None:
    log_path = _write_log(tmp_path, "app.jsonl", _as_jsonl(VALID_LINES))

    records, summary = process_log_file(log_path)

    assert records == [
        LogRecord(
            level="INFO",
            service="payment-api",
            message="charge succeeded",
            line_number=1,
        ),
        LogRecord(
            level="ERROR",
            service="payment-api",
            message="charge failed",
            line_number=2,
        ),
        LogRecord(
            level="WARNING", service="auth", message="slow login", line_number=3
        ),
    ]
    assert summary.total_lines == 3
    assert summary.processed_count == 3
    assert summary.skipped_count == 0
    assert summary.errors == ()


def test_blank_lines_are_ignored_not_errors(tmp_path: Path) -> None:
    lines = ["", "   ", _as_jsonl(VALID_LINES[:1])[0], ""]
    log_path = _write_log(tmp_path, "gappy.jsonl", lines)

    records, summary = process_log_file(log_path)

    assert len(records) == 1
    assert summary.total_lines == 1
    assert summary.skipped_count == 0


def test_iter_yields_only_valid_records(tmp_path: Path) -> None:
    lines = [
        _as_jsonl(VALID_LINES[:1])[0],
        "{not json",
        _as_jsonl(VALID_LINES[1:2])[0],
    ]
    log_path = _write_log(tmp_path, "mixed.jsonl", lines)

    assert [record.service for record in iter_log_records(log_path)] == [
        "payment-api",
        "payment-api",
    ]


def test_malformed_json_line_is_skipped_and_counted(tmp_path: Path) -> None:
    lines = [
        _as_jsonl(VALID_LINES[:1])[0],
        "{not json",
        _as_jsonl(VALID_LINES[1:])[0],
        _as_jsonl(VALID_LINES[2:])[0],
    ]
    log_path = _write_log(tmp_path, "bad-line.jsonl", lines)

    records, summary = process_log_file(log_path)

    assert len(records) == 3
    assert summary.total_lines == 4
    assert summary.processed_count == 3
    assert summary.skipped_count == 1
    assert len(summary.errors) == 1
    assert summary.errors[0].line_number == 2
    assert "Invalid JSON" in summary.errors[0].reason
    assert summary.errors[0].raw == "{not json"


def test_non_object_line_is_skipped(tmp_path: Path) -> None:
    lines = [_as_jsonl(VALID_LINES[:1])[0], "[1, 2, 3]", '"just a string"']
    log_path = _write_log(tmp_path, "non-object.jsonl", lines)

    _, summary = process_log_file(log_path)

    assert summary.processed_count == 1
    assert summary.skipped_count == 2
    assert all("Expected a JSON object" in e.reason for e in summary.errors)


def test_missing_message_is_skipped(tmp_path: Path) -> None:
    record = {"level": "INFO", "service": "payment-api"}
    lines = [_as_jsonl(VALID_LINES[:1])[0], json.dumps(record)]
    log_path = _write_log(tmp_path, "missing-message.jsonl", lines)

    _, summary = process_log_file(log_path)

    assert summary.processed_count == 1
    assert summary.skipped_count == 1
    assert summary.errors[0].reason == "Missing required field 'message'"


def test_unknown_level_is_skipped(tmp_path: Path) -> None:
    record = {"level": "TRACE", "service": "payment-api", "message": "trace"}
    lines = [_as_jsonl(VALID_LINES[:1])[0], json.dumps(record)]
    log_path = _write_log(tmp_path, "unknown-level.jsonl", lines)

    _, summary = process_log_file(log_path)

    assert summary.processed_count == 1
    assert summary.skipped_count == 1
    assert "Unknown log level" in summary.errors[0].reason


def test_level_is_normalised_to_uppercase(tmp_path: Path) -> None:
    record = {"level": "info", "service": "payment-api", "message": "lowercase"}
    log_path = _write_log(tmp_path, "lowercase.jsonl", [json.dumps(record)])

    records, _ = process_log_file(log_path)

    assert records[0].level == "INFO"


def test_extra_fields_are_preserved(tmp_path: Path) -> None:
    record = {**VALID_LINES[0], "trace_id": "abc-123", "latency_ms": 42}
    log_path = _write_log(tmp_path, "extra.jsonl", [json.dumps(record)])

    records, _ = process_log_file(log_path)

    assert records[0].extra == {"trace_id": "abc-123", "latency_ms": 42}


def test_missing_file_raises_and_chains(tmp_path: Path) -> None:
    log_path = tmp_path / "missing.jsonl"

    with pytest.raises(LogFileReadError, match="Could not read") as error:
        process_log_file(log_path)

    assert isinstance(error.value.__cause__, FileNotFoundError)


def test_invalid_utf8_raises_and_chains(tmp_path: Path) -> None:
    log_path = tmp_path / "invalid-encoding.jsonl"
    log_path.write_bytes(b'{"level": "INFO", \xff}\n')

    with pytest.raises(LogFileReadError, match="not valid UTF-8") as error:
        process_log_file(log_path)

    assert isinstance(error.value.__cause__, UnicodeDecodeError)


def test_error_types_are_distinct(tmp_path: Path) -> None:
    log_path = tmp_path / "missing.jsonl"

    with pytest.raises(LogFileReadError):
        list(iter_log_records(log_path))

    with pytest.raises(LogFileReadError):
        process_log_file(log_path)

    assert issubclass(LogFileReadError, LogFileError)
    assert not issubclass(LogLineError, Exception)
