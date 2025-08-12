#!/bin/bash
# Backend Build Script
set -e

echo "Installing backend dependencies..."
pip install -r requirements.lock

echo "Running linting..."
ruff check .
black --check .
isort --check-only .

echo "Running tests..."
pytest -v

echo "Backend build completed successfully!"
