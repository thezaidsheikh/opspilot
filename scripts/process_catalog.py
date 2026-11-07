"""Run the catalog processor against the sample dataset."""

import json
from pathlib import Path

from opspilot.catalog import CatalogProcessor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "products.json"


def main() -> None:
    """Process the sample product catalog."""
    with DATA_PATH.open(encoding="utf-8") as file:
        records = json.load(file)

    processor = CatalogProcessor.from_records(records)
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


if __name__ == "__main__":
    main()
