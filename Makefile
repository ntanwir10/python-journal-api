.PHONY: help install dev test lint format clean

help: ## Show this help menu
	@echo 'Available commands:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn app.main:app --reload --port 8000

test: ## Run tests
	pytest -v --cov=app

lint: ## Check code style
	flake8 .
	black . --check

format: ## Format code
	black .
	isort .

clean: ## Remove cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 