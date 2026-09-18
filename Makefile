.PHONY: check lint format typecheck test lengths demo

check: lint typecheck test

lint:
	ruff check src tests worlds examples tools
	ruff format --check src tests worlds examples tools
	python tools/check_file_length.py

format:
	ruff format src tests worlds examples tools
	ruff check --fix src tests worlds examples tools

typecheck:
	python -m mypy

test:
	python -m pytest -q tests

lengths:
	python tools/check_file_length.py

demo:
	python examples/demo.py
