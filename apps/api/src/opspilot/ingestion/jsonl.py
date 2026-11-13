"""Robust JSON Lines (JSONL) log processing for incident ingestion.

Two error layers, by design:

* File-level errors raise. A missing file, an unreadable file, or a file
  that is not valid UTF-8 means the run cannot start, so ``LogFileReadError``
  is raised (chained to the original error with ``from exc``). Silently
  returning an empty result would hide a real problem.
* Line-level errors are skipped, logged, and counted. One bad line in a
  10,000-line log file must never kill the whole batch, so a malformed line
  becomes a ``LogLineError`` in the summary and processing continues.

Blank lines are ignored — they are neither processed nor errors.
``total_lines`` counts non-blank lines only, so ``processed_count`` +
``skipped_count`` always equals ``total_lines``.
"""

import json
import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
REQUIRED_FIELDS = ("level", "service", "message")


class LogFileError(Exception):
    """Base error for log file processing."""


class LogFileReadError(LogFileError):
    """The log file could not be read as UTF-8 text."""


@dataclass(frozen=True)
class LogRecord:
    """One validated log record from a JSONL file."""

    level: str
    service: str
    message: str
    line_number: int
    extra: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LogLineError:
    """One log line that was skipped, with the reason why."""

    line_number: int
    reason: str
    raw: str


@dataclass(frozen=True)
class LogProcessingSummary:
    """Counts for one processed log file."""

    total_lines: int
    processed_count: int
    skipped_count: int
    errors: tuple[LogLineError, ...] = ()


def _parse_line(raw: str, line_number: int) -> LogRecord | LogLineError:
    """Validate one JSONL line, returning a record or the skip reason."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return LogLineError(
            line_number=line_number,
            reason=f"Invalid JSON: {exc.msg} (column {exc.colno})",
            raw=raw,
        )

    if not isinstance(payload, dict):
        return LogLineError(
            line_number=line_number,
            reason=f"Expected a JSON object; found {type(payload).__name__}",
            raw=raw,
        )

    for field_name in REQUIRED_FIELDS:
        if field_name not in payload:
            return LogLineError(
                line_number=line_number,
                reason=f"Missing required field '{field_name}'",
                raw=raw,
            )

    level = payload["level"]
    if not isinstance(level, str) or level.upper() not in LOG_LEVELS:
        return LogLineError(
            line_number=line_number,
            reason=f"Unknown log level: {level!r}",
            raw=raw,
        )

    for field_name in ("service", "message"):
        value = payload[field_name]
        if not isinstance(value, str) or not value.strip():
            return LogLineError(
                line_number=line_number,
                reason=f"Field '{field_name}' must be a non-empty string",
                raw=raw,
            )

    extra = {
        key: value
        for key, value in payload.items()
        if key not in REQUIRED_FIELDS
    }
    return LogRecord(
        level=level.upper(),
        service=payload["service"].strip(),
        message=payload["message"].strip(),
        line_number=line_number,
        extra=extra,
    )


def _iter_parsed_lines(path: Path) -> Iterator[LogRecord | LogLineError]:
    """Yield each non-blank line as a record or a skip reason.

    File-level problems raise ``LogFileReadError``; line-level problems are
    yielded as ``LogLineError`` values so the caller can decide what to do.
    """
    try:
        file = path.open("r", encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise LogFileReadError(f"Log file is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise LogFileReadError(f"Could not read log file {path}: {exc}") from exc

    with file:
        for line_number, line in enumerate(file, start=1):
            raw = line.strip()
            if not raw:
                continue
            parsed = _parse_line(raw, line_number)
            if isinstance(parsed, LogLineError):
                logger.warning(
                    "Skipping line %d in %s: %s",
                    line_number,
                    path,
                    parsed.reason,
                )
            yield parsed


def iter_log_records(path: Path) -> Iterator[LogRecord]:
    """Yield one good log record at a time, lazily.

    Bad lines are skipped (and logged as warnings) instead of stopping the
    run, so a huge file is never loaded fully into memory. Use
    :func:`process_log_file` when you also need the skip counts.
    """
    for parsed in _iter_parsed_lines(path):
        if isinstance(parsed, LogRecord):
            yield parsed


def process_log_file(path: Path) -> tuple[list[LogRecord], LogProcessingSummary]:
    """Process a whole JSONL log file, returning records and a summary.

    The summary counts let the caller check what happened instead of
    guessing: ``processed_count`` + ``skipped_count`` == ``total_lines``.
    """
    records: list[LogRecord] = []
    errors: list[LogLineError] = []

    for parsed in _iter_parsed_lines(path):
        if isinstance(parsed, LogRecord):
            records.append(parsed)
        else:
            errors.append(parsed)

    summary = LogProcessingSummary(
        total_lines=len(records) + len(errors),
        processed_count=len(records),
        skipped_count=len(errors),
        errors=tuple(errors),
    )
    logger.info(
        "Processed %s: %d records, %d skipped lines",
        path,
        summary.processed_count,
        summary.skipped_count,
    )
    return records, summary
