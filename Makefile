.PHONY: install dev test lint format docker-up

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

docker-up:
	docker compose up --build
