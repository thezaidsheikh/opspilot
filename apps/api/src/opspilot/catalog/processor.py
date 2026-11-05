"""Collection-based product catalog processing."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Product:
    """Immutable representation of a catalog product."""

    id: str
    name: str
    category: str
    price: float
    active: bool
    tags: tuple[str, ...]


@dataclass(frozen=True)
class CatalogSummary:
    """Summary statistics for a product catalog."""

    total_products: int
    active_products: int
    categories: tuple[str, ...]
    average_active_price: float


class CatalogProcessor:
    """Processes product records using Python collections."""

    def __init__(self, products: list[Product]) -> None:
        self._products = tuple(products)

    @classmethod
    def from_records(
        cls,
        records: list[dict[str, Any]],
    ) -> "CatalogProcessor":
        """Convert input dictionaries into domain objects."""
        products = [
            Product(
                id=record["id"],
                name=record["name"],
                category=record["category"],
                price=float(record["price"]),
                active=record["active"],
                tags=tuple(record.get("tags", [])),
            )
            for record in records
        ]

        return cls(products)

    def active_products(self) -> list[Product]:
        """Return products currently active in the catalog."""
        return [product for product in self._products if product.active]

    def products_by_category(
        self,
        category: str,
    ) -> list[Product]:
        """Filter products by category."""
        return [product for product in self._products if product.category == category]

    def find_by_id(self, product_id: str) -> Product | None:
        """Find one product by its unique identifier."""
        product_index = {product.id: product for product in self._products}

        return product_index.get(product_id)

    def unique_categories(self) -> set[str]:
        """Return all distinct catalog categories."""
        return {product.category for product in self._products}

    def products_by_tag(self, tag: str) -> list[Product]:
        """Find products containing a particular tag."""
        return [product for product in self._products if tag in product.tags]

    def summary(self) -> CatalogSummary:
        """Calculate catalog statistics."""
        active = self.active_products()

        average_price = (
            sum(product.price for product in active) / len(active) if active else 0.0
        )

        return CatalogSummary(
            total_products=len(self._products),
            active_products=len(active),
            categories=tuple(sorted(self.unique_categories())),
            average_active_price=round(average_price, 2),
        )
