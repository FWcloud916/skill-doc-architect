.PHONY: run test lint

run:
	PYTHONPATH=src python -m atlas_cli.main

test:
	PYTHONPATH=src python -m unittest discover -s tests

lint:
	ruff check src tests
