# OpsPilot — Persistent Project Context

Last verified: 2026-11-07

Repository: https://github.com/thezaidsheikh/opspilot

Default branch: master

## Project Goal

Build OpsPilot, an AI Incident Investigation & Remediation Platform, while following the authoritative 72-day Applied AI Engineering roadmap.

## Current Learning Stage

Python and Software Engineering Foundations.

The repository contains the initial Python project skeleton and a product catalog processing exercise.

Do not assume every Day 1 and Day 2 learning outcome has been assessed or completed merely because the repository exists.

## Verified Repository Structure

```text
opspilot/
├── apps/
│   └── api/
│       └── src/
│           └── opspilot/
│               ├── __init__.py
│               ├── main.py
│               └── catalog/
│                   ├── __init__.py
│                   └── processor.py
├── data/
│   └── products.json
├── docs/
├── scripts/
│   └── process_catalog.py
├── tests/
│   └── unit/
│       └── test_catalog.py
├── .gitignore
├── README.md
├── pytest.ini
└── pyrightconfig.json
```

## Verified Existing Implementation

### Python Package

`apps/api/src/opspilot/`

### Main Module

`apps/api/src/opspilot/main.py`

### Catalog Domain

`apps/api/src/opspilot/catalog/processor.py`

Contains:

- Product dataclass
- CatalogSummary dataclass
- CatalogProcessor
- active_products()
- products_by_category()
- find_by_id()
- unique_categories()
- products_by_tag()
- summary()
- filter_products()

### Sample Data

`data/products.json`

### Script

`scripts/process_catalog.py`

### Tests

`tests/unit/test_catalog.py`

### Existing Commit History

- Initial Python project skeleton.
- Catalog module and unit tests.
- Catalog processing script and pytest configuration.
- filter_products implementation.

## Existing Technical Observations

- The package uses a source layout under `apps/api/src`.
- `pytest.ini` configures the Python import path.
- `pyrightconfig.json` configures source and test paths.
- The catalog uses dataclasses and collection-based processing.
- `filter_products()` currently has non-standard parameter names (`minPrice`, `catagory`); consider correcting them during the appropriate implementation review.
- Input records currently use `dict[str, Any]`; stronger boundary validation is a future typing/Pydantic learning objective.
- The original README was empty.

## Architecture Direction

The eventual target architecture includes:

- Next.js dashboard
- FastAPI and Pydantic backend
- Authentication and tenant isolation
- LangGraph workflows
- PostgreSQL and pgvector
- LLM and embedding providers
- Read-only diagnostic tools
- Redis and background ingestion jobs
- Langfuse, OpenTelemetry, and Prometheus
- pytest, custom evaluation, and RAGAS
- Docker, GitHub Actions, and cloud deployment

These are planned capabilities, not claims about the current implementation.

## Current Setup Priorities

1. Establish Python package metadata.
2. Establish reproducible development dependencies.
3. Configure linting and formatting.
4. Configure type checking.
5. Configure pytest.
6. Add local development commands.
7. Add GitHub Actions CI.
8. Document architecture and project conventions.

## Future Work

Implement roadmap topics in their prescribed order.

Do not prematurely add future-stage frameworks or infrastructure.

## Daily Progress Log

Update this section after each study day.

| Day | Status                                                   | Deliverable                                   | Assessment                               |
| --- | -------------------------------------------------------- | --------------------------------------------- | ---------------------------------------- |
| 1   | Repository skeleton present; learning assessment pending | Initial Python project                        | Pending verification                     |
| 2   | Learning assessment pending                              | Variables, types, strings and transformations | Pending verification                     |
| 3   | Implementation present                                   | Catalog processor and collections             | Verify tests and interview understanding |

## Next Step

Verify the foundational configuration and current Python exercises, then continue the next pending roadmap day.

## Progress Update Template

### Day:

### Concepts Completed:

### Files Created or Changed:

### Implementation:

### Tests Executed:

### Test Results:

### Interview Questions Reviewed:

### Assessment Score:

### Gaps / Catch-up:

### Commit:

### Next Step:
