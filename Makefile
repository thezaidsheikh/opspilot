
PYTHON ?= python3
VENV_DIR ?= .venv

VENV_PYTHON := $(VENV_DIR)/bin/python
RUFF := $(VENV_DIR)/bin/ruff
PYRIGHT := $(VENV_DIR)/bin/pyright


.PHONY: venv install setup test coverage lint format format-check typecheck check run-catalog clean


venv:
	$(PYTHON) -m venv $(VENV_DIR)


install: venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e ".[dev]"


setup: install


test:
	$(VENV_PYTHON) -m pytest


coverage:
	$(VENV_PYTHON) -m pytest --cov=opspilot --cov-report=term-missing


lint:
	$(RUFF) check .


format:
	$(RUFF) format .


format-check:
	$(RUFF) format --check .


typecheck:
	$(PYRIGHT)


check: lint format-check typecheck test


run-catalog:
	$(VENV_PYTHON) scripts/process_catalog.py


clean:
	rm -rf .pytest_cache .ruff_cache .pyright .coverage htmlcov
