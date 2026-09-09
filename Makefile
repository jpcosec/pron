PYTHON ?= python

.PHONY: check lint format-check format typecheck test docs-check

check:
	$(MAKE) lint format-check typecheck
	$(MAKE) test
	$(MAKE) docs-check

lint:
	$(PYTHON) -m ruff check src tests

format-check:
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff format src tests

typecheck:
	$(PYTHON) -m mypy

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest -q

docs-check:
	$(PYTHON) -m pron.cli.main docs --world . --pythonpath . --check
	$(PYTHON) -m pron.cli.main check --world . --pythonpath .
