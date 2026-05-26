.PHONY: run run-example test lint typecheck

run:
	python -m src.server

run-example:
	FLEET_DATA_DIR=tests/fixtures/example-fleet python -m src.server

test:
	python -m pytest tests/ -x -q --tb=short

lint:
	ruff check src/ tests/

typecheck:
	mypy src/
