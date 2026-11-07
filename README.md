# OpsPilot

**AI Incident Investigation & Remediation Platform**

OpsPilot is a production-oriented Applied AI engineering project designed to help engineering teams investigate software incidents using internal knowledge, diagnostic tools, and evidence-backed AI workflows.

The project is being developed incrementally as part of a structured 72-day Applied AI Engineering curriculum.

## Project Vision

Production incidents often require engineers to inspect multiple sources:

- Application logs
- Infrastructure metrics
- Deployment history
- Service health
- Runbooks
- Previous incident reports
- Internal engineering documentation

OpsPilot aims to bring these sources into one AI-assisted investigation workflow.

It will retrieve relevant knowledge, run read-only diagnostics, generate evidence-backed root-cause hypotheses, and require human approval before risky remediation.

## Planned Capabilities

1. Document ingestion and knowledge management
2. Retrieval-Augmented Generation (RAG)
3. Grounded answers with source citations
4. Read-only diagnostic tools
5. AI-powered incident investigation
6. Root-cause hypotheses with supporting evidence
7. Human approval for remediation
8. AI evaluation and observability dashboard
9. Production deployment and monitoring

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic

### AI Engineering

- LLM APIs
- Embeddings
- PostgreSQL + pgvector
- LangGraph
- RAG evaluation

### Infrastructure

- Redis
- Background jobs
- Docker
- GitHub Actions

### Observability and Evaluation

- Langfuse
- OpenTelemetry
- Prometheus
- pytest
- Custom evaluation harness
- RAGAS

### Frontend

- Next.js
- React
- TypeScript

These technologies will be introduced at the appropriate stages of the curriculum. Not all planned components are implemented yet.

## Current Repository Structure

```text
opspilot/
├── apps/
│   └── api/
│       └── src/
│           └── opspilot/
├── data/
├── docs/
├── scripts/
├── tests/
├── pyproject.toml
├── pytest.ini
├── pyrightconfig.json
└── README.md
```

## Prerequisites

- Python 3.12 or 3.13
- Git
- Make (optional, for convenient commands)

## Local Setup

Clone the repository:

```bash
git clone https://github.com/thezaidsheikh/opspilot.git

cd opspilot
```

Create the virtual environment and install dependencies:

```bash
make install
```

Alternatively, use:

```bash
python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

python -m pip install -e ".[dev]"
```

## Run the Current Example

```bash
make run-catalog
```

Or:

```bash
python scripts/process_catalog.py
```

## Run Tests

```bash
make test
```

## Run Quality Checks

```bash
make check
```

Individual commands:

```bash
ruff check .

ruff format --check .

pyright

pytest
```

## Engineering Principles

OpsPilot follows:

- Object-oriented programming where appropriate
- SOLID principles
- Composition over unnecessary inheritance
- Modular monolith architecture
- Clear domain boundaries
- Type-safe Python
- Dependency injection
- Automated testing
- Secure configuration management
- Structured logging and error handling
- Production-oriented engineering practices

We will avoid premature microservices and unnecessary abstractions.

## Architecture

The target architecture is documented in:

`docs/architecture/overview.md`

Architectural decisions should be recorded under:

`docs/adr/`

## Learning and Implementation Roadmap

The project follows the authoritative 72-day Applied AI Engineering roadmap.

Every study day should produce a meaningful implementation, test, documentation update, or assessment artifact.

## Current Status

The repository is in its Python foundations stage.

Existing implementation includes:

- Python package structure
- Product catalog domain models
- Collection-based processing
- Catalog summary calculations
- Unit tests

Future AI and production capabilities are planned, not yet implemented.

## Safety

Diagnostic tools are read-only by default.

Risky remediation must require explicit human approval.

Never commit API keys, passwords, access tokens, or production credentials.

## License

No open-source license has been selected yet. All rights remain with the repository owner unless a license is added.
