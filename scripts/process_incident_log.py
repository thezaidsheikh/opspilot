"""Run the incident log processor against a JSONL log file.

Malformed lines are skipped with a warning, never fatal: the exit code
stays 0 as long as the file itself could be read. Only a file-level
problem (missing file, unreadable, not UTF-8) exits non-zero.
"""

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from opspilot.ingestion import LogFileError, process_log_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "incident-log-sample.jsonl"
logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Process the selected incident log and return a process exit code."""
    parser = argparse.ArgumentParser(
        description="Process a JSONL incident log, skipping malformed lines."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="show debug details such as each processed record",
    )
    parser.add_argument(
        "log_file",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"JSONL log file (default: {DEFAULT_DATA_PATH})",
    )
    args = parser.parse_args(argv)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        records, summary = process_log_file(args.log_file)
    except LogFileError as exc:
        logger.error("Incident log processing failed: %s", exc)
        return 2

    print("Incident Log Summary")
    print(f"Total lines: {summary.total_lines}")
    print(f"Processed: {summary.processed_count}")
    print(f"Skipped: {summary.skipped_count}")

    if summary.errors:
        print("\nSkipped lines")
        for error in summary.errors:
            print(f"- line {error.line_number}: {error.reason}")

    if args.verbose:
        print("\nProcessed records")
        for record in records:
            print(f"- [{record.level}] {record.service}: {record.message}")

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
