.PHONY: help install dev-install test lint format type-check clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run pylint"
	@echo "  format       - Format code with black and isort"
	@echo "  format-check - Check code formatting"
	@echo "  type-check   - Run mypy type checking"
	@echo "  clean        - Clean cache and build files"
	@echo "  quality      - Run all quality checks (lint + format-check + type-check)"

# Install dependencies
install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

# Testing
test:
	pytest --cov=backend --cov-report=html --cov-report=term-missing

test-fast:
	pytest -x --no-cov

# Code quality
lint:
	pylint backend/

format:
	black backend/
	isort backend/

format-check:
	black --check backend/
	isort --check-only backend/

type-check:
	mypy backend/

# Combined quality check
quality: format-check lint type-check
	@echo "All quality checks passed!"

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Development server
dev:
	python -m flask run --debug

# Database migrations (if using Flask-Migrate)
migrate:
	flask db migrate

upgrade:
	flask db upgrade

downgrade:
	flask db downgrade