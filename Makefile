.PHONY: help lint typecheck test test-cov format check clean install install-dev

# Default target
help:
	@echo "Available targets:"
	@echo "  help         Show this help message"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  lint         Run ruff linter"
	@echo "  format       Run ruff formatter"
	@echo "  typecheck    Run mypy type checker"
	@echo "  test         Run pytest tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  check        Run all checks (lint + typecheck + test)"
	@echo "  clean        Clean cache and temporary files"

# Installation targets
install:
	uv sync --no-dev

install-dev:
	uv sync --extra dev --extra test

# Code quality targets
lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

# Testing targets
test:
	uv run pytest

test-cov:
	uv run pytest --cov=src/boatmcp --cov-report=term-missing --cov-report=xml

# Combined check target
check: lint typecheck test

# Cleanup target
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -f coverage.xml
	rm -f .coverage