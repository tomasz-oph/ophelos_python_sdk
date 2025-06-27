# Ophelos SDK Development Makefile
.PHONY: help install install-dev test test-cov lint format check clean build upload docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run all linting tools"
	@echo "  format       Format code with black and isort"
	@echo "  check        Run all code quality checks"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo "  upload       Upload to PyPI (requires credentials)"
	@echo "  docs         Generate documentation"
	@echo "  pre-commit   Install and run pre-commit hooks"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	python -m pytest

test-cov:
	python -m pytest --cov=ophelos_sdk --cov-report=html --cov-report=term-missing

# Code quality
lint:
	@echo "Running autoflake..."
	python -m autoflake --check --recursive --remove-all-unused-imports --remove-unused-variables ophelos_sdk/ tests/ examples/
	@echo "Running isort..."
	python -m isort --check-only --diff ophelos_sdk/ tests/ examples/
	@echo "Running black..."
	python -m black --check ophelos_sdk/ tests/ examples/
	@echo "Running flake8..."
	python -m flake8 ophelos_sdk/ tests/ examples/
	@echo "Running mypy..."
	python -m mypy ophelos_sdk/

format:
	@echo "Running autoflake..."
	python -m autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables ophelos_sdk/ tests/ examples/
	@echo "Running isort..."
	python -m isort ophelos_sdk/ tests/ examples/
	@echo "Running black..."
	python -m black ophelos_sdk/ tests/ examples/

check: lint test

# Pre-commit
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine check dist/*
	python -m twine upload dist/*

# Documentation
docs:
	@echo "Documentation generation not yet configured"
	@echo "Consider using mkdocs: pip install mkdocs mkdocs-material"

# Development workflow
dev-setup: install-dev pre-commit
	@echo "Development environment setup complete!"

# Quick development check
dev-check: format lint test
	@echo "All development checks passed!"
