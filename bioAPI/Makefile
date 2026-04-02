.PHONY: run dev test lint format clean docker-build docker-run

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --reload

test:
	pytest tests/ -v

lint:
	ruff check .
	mypy app

format:
	black .
	ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t bioAPI .

docker-run:
	docker run -p 8000:8000 --env-file .env bioAPI
