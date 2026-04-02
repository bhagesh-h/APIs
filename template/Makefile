.PHONY: dev test lint format typecheck docker-build docker-run clean

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	black .
	ruff check --fix .

typecheck:
	mypy app

docker-build:
	docker build -t fastapi-template .

docker-run:
	docker run -p 8000:8000 --env-file .env fastapi-template

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
