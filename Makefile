.PHONY: install test lint type-check run docker-up docker-down clean

install:
	pip install -r backend/requirements.txt

test:
	pytest backend/app/tests -v

test-cov:
	pytest backend/app/tests --cov=backend/app --cov-report=html

lint:
	ruff check backend/app

type-check:
	mypy backend/app

format:
	black backend/app

run:
	uvicorn backend.app.main:app --reload

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
