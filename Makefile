PYTHON ?= python

.PHONY: check lint audit format-check format typecheck test world docs-check

check:
	$(MAKE) lint format-check typecheck
	$(MAKE) test
	$(MAKE) docs-check

lint:
	$(PYTHON) -m ruff check src tests

# standards.md Layer 1 (size/structure), report-only until the backlog is collapsed
audit:
	$(PYTHON) -m ruff check src --select C901,PLR0911,PLR0912,PLR0915 --exit-zero --output-format concise
	$(PYTHON) scripts/check_file_length.py src --report

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
