.PHONY: help install dev test lint typecheck migrate migrate-down seed run clean

help:
	@echo "ZAVOD EMPIRE BOT - Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Install dev dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run code linter"
	@echo "  make typecheck     - Run mypy type checker"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-down  - Rollback last migration"
	@echo "  make seed          - Seed initial data"
	@echo "  make run           - Run bot in development mode"
	@echo "  make clean         - Clean cache and compiled files"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	pytest tests/ -v --cov=bot --cov-report=html

lint:
	flake8 bot/ tests/ --max-line-length=120 --ignore=E203,W503

typecheck:
	mypy bot/ --ignore-missing-imports

migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

seed:
	python -m bot.scripts.seed_data

run:
	python -m bot --mode polling

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/ build/ *.egg-info/

docker-build:
	docker-compose -f docker-compose.dev.yml build

docker-up:
	docker-compose -f docker-compose.dev.yml up -d

docker-down:
	docker-compose -f docker-compose.dev.yml down

docker-logs:
	docker-compose -f docker-compose.dev.yml logs -f bot-worker
