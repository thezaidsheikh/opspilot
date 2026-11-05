from opspilot.catalog import CatalogProcessor, Product

SAMPLE_RECORDS = [
    {
        "id": "prod-001",
        "name": "API Monitoring",
        "category": "observability",
        "price": 49.99,
        "active": True,
        "tags": ["monitoring", "api"],
    },
    {
        "id": "prod-002",
        "name": "Log Analyzer",
        "category": "observability",
        "price": 29.99,
        "active": True,
        "tags": ["logs", "debugging"],
    },
    {
        "id": "prod-003",
        "name": "Legacy Dashboard",
        "category": "analytics",
        "price": 19.99,
        "active": False,
        "tags": ["dashboard"],
    },
]


def create_processor() -> CatalogProcessor:
    return CatalogProcessor.from_records(SAMPLE_RECORDS)


def test_active_products() -> None:
    processor = create_processor()

    result = processor.active_products()

    assert len(result) == 2
    assert all(product.active for product in result)


def test_products_by_category() -> None:
    processor = create_processor()

    result = processor.products_by_category("observability")

    assert len(result) == 2


def test_find_by_id() -> None:
    processor = create_processor()

    result = processor.find_by_id("prod-001")

    assert result is not None
    assert result.name == "API Monitoring"


def test_find_missing_id() -> None:
    processor = create_processor()

    assert processor.find_by_id("missing") is None


def test_unique_categories() -> None:
    processor = create_processor()

    assert processor.unique_categories() == {
        "observability",
        "analytics",
    }


def test_products_by_tag() -> None:
    processor = create_processor()

    result = processor.products_by_tag("monitoring")

    assert [product.id for product in result] == ["prod-001"]


def test_summary() -> None:
    processor = create_processor()

    result = processor.summary()

    assert result.total_products == 3
    assert result.active_products == 2
    assert result.categories == ("analytics", "observability")
    assert result.average_active_price == 39.99


def test_empty_catalog() -> None:
    processor = CatalogProcessor([])

    result = processor.summary()

    assert result.total_products == 0
    assert result.active_products == 0
    assert result.average_active_price == 0.0


def test_product_is_immutable() -> None:
    product = Product(
        id="prod-001",
        name="API Monitoring",
        category="observability",
        price=49.99,
        active=True,
        tags=("monitoring",),
    )

    try:
        product.name = "Changed"
        assert False, "Expected immutable product"
    except AttributeError:
        pass
