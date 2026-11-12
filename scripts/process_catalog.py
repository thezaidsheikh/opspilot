"""Run the catalog processor against a JSON dataset."""

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from opspilot.catalog import CatalogFileError, CatalogProcessor, load_catalog_records

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "products.json"
logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Process the selected product catalog and return a process exit code."""
    parser = argparse.ArgumentParser(
        description="Validate and summarize a product catalog."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="show debug details such as the loaded record count",
    )
    parser.add_argument(
        "catalog",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"JSON catalog file (default: {DEFAULT_DATA_PATH})",
    )
    args = parser.parse_args(argv)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        records = load_catalog_records(args.catalog)
        processor = CatalogProcessor.from_records(records)
    except CatalogFileError as exc:
        logger.error("Catalog processing failed: %s", exc)
        return 2
    except (KeyError, TypeError, ValueError) as exc:
        # Protect the CLI boundary if processor validation evolves independently.
        logger.error("Catalog records could not be processed: %s", exc)
        return 2

    summary = processor.summary()
    print("Catalog Summary")
    print(f"Total products: {summary.total_products}")
    print(f"Active products: {summary.active_products}")
    print(f"Categories: {', '.join(summary.categories)}")
    print(f"Average active price: ${summary.average_active_price:.2f}")

    print("\nActive Products")
    for product in processor.active_products():
        print(f"- {product.name} (${product.price:.2f})")

    print("\nFiltered Products")
    for product in processor.filter_products(
        minPrice=25.0,
        catagory="observability",
    ):
        print(f"- {product.name} (${product.price:.2f})")

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
