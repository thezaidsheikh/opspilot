"""Validated JSON file input for product catalog records."""

import json
import logging
import math
from pathlib import Path

logger = logging.getLogger(__name__)
type JsonValue = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)


class CatalogFileError(Exception):
    """Base error for catalog file loading and validation."""


class CatalogFileReadError(CatalogFileError):
    """The catalog file could not be read as UTF-8 text."""


class CatalogJsonError(CatalogFileError):
    """The catalog file does not contain valid JSON."""


class CatalogStructureError(CatalogFileError):
    """The JSON value does not match the catalog record structure."""


def load_catalog_records(path: Path) -> list[dict[str, object]]:
    """Read and validate a JSON array of product records from ``path``.

    Required fields are ``id``, ``name``, ``category``, ``price``, and
    ``active``. ``tags`` is optional and defaults to an empty list, matching
    ``CatalogProcessor.from_records``. Extra fields are preserved and ignored
    by the current processor.
    """
    try:
        with path.open("r", encoding="utf-8") as file:
            payload: JsonValue = json.load(file)
    except UnicodeDecodeError as exc:
        raise CatalogFileReadError(f"Catalog file is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise CatalogFileReadError(
            f"Could not read catalog file {path}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise CatalogJsonError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    records = _validate_records(payload, path)
    logger.debug("Loaded %d catalog records from %s", len(records), path)
    return records


def _validate_records(payload: JsonValue, path: Path) -> list[dict[str, object]]:
    if not isinstance(payload, list):
        raise CatalogStructureError(
            f"Expected a JSON array of product records in {path}; "
            f"found {type(payload).__name__}"
        )

    validated: list[dict[str, object]] = []
    required_fields = ("id", "name", "category", "price", "active")
    for index, value in enumerate(payload):
        location = f"{path}: record {index}"
        if not isinstance(value, dict):
            raise CatalogStructureError(
                f"Expected an object at {location}; found {type(value).__name__}"
            )

        for field in required_fields:
            if field not in value:
                raise CatalogStructureError(
                    f"Missing required field '{field}' at {location}"
                )

        for field in ("id", "name", "category"):
            field_value = value[field]
            if not isinstance(field_value, str) or not field_value.strip():
                raise CatalogStructureError(
                    f"Field '{field}' must be a non-empty string at {location}"
                )

        price = value["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise CatalogStructureError(f"Field 'price' must be a number at {location}")
        if not math.isfinite(price):
            raise CatalogStructureError(f"Field 'price' must be finite at {location}")

        if not isinstance(value["active"], bool):
            raise CatalogStructureError(
                f"Field 'active' must be a boolean at {location}"
            )

        tags = value.get("tags", [])
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise CatalogStructureError(
                f"Field 'tags' must be an array of strings at {location}"
            )

        validated.append(dict(value))

    return validated
