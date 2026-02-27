.PHONY: run test lint

run:
	py -m uvicorn app.main:app --reload

test:
	py -m pytest

lint:
	py -m ruff check app tests
