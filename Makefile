.PHONY: help install dev test lint format clean setup db-setup db-migrate db-upgrade db-downgrade

help: ## Show this help menu
	@echo 'Available commands:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment and install dependencies
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install: ## Install project dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn app.main:app --reload --port 8000

test: ## Run tests
	pytest -v --cov=app tests/

lint: ## Check code style
	flake8 app/ tests/ --exclude=venv/
	black . --check --exclude=venv/

format: ## Format code
	black . --exclude=venv/
	isort . --skip=venv/

clean: ## Remove cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

db-setup: ## Setup databases and extensions
	chmod +x scripts/setup_db.sh
	./scripts/setup_db.sh

db-migrate: ## Create a new database migration
	alembic revision --autogenerate -m "$(message)"

db-upgrade: ## Apply all pending migrations
	alembic upgrade head

db-downgrade: ## Rollback the last migration
	alembic downgrade -1 