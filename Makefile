PYTHON ?= python

.PHONY: check lint format-check format typecheck test world docs-check

check:
	$(MAKE) lint format-check typecheck
	$(MAKE) test
	$(MAKE) docs-check

# includes standards.md Layer 1 for src/ and tests/: ≤10 statements per function, ≤100 code lines per file
lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) tools/check_file_length.py src tests

format-check:
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff format src tests

typecheck:
	$(PYTHON) -m mypy

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest -q -p syrupy

# pron's own world is derived: rebuild the store and the generated docs from the repo
world:
	test -f .sldb/core/store_index.yaml || sldb stores init
	$(PYTHON) -m pron.cli.main init --world . --pythonpath . --knowledge > /dev/null
	$(PYTHON) -m pron.cli.main docs --world . --pythonpath .

docs-check: world
	git diff --exit-code -- README.md
	$(PYTHON) -m pron.cli.main docs --world . --pythonpath . --check
	$(PYTHON) -m pron.cli.main check --world . --pythonpath .
