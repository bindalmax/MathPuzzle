.PHONY: help clean install test build run docker-build lint format

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:
	@echo "Available targets:"
	@echo "  make clean          - Remove build artifacts, cache, and virtual environment"
	@echo "  make install        - Create venv and install dependencies"
	@echo "  make test           - Run tests"
	@echo "  make build          - Clean, install, and test (full cycle)"
	@echo "  make run            - Run Flask app locally"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make lint           - Run linting checks"
	@echo "  make format         - Auto-format code"

clean:
	rm -rf __pycache__ .pytest_cache instance build dist *.egg-info
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete"

install: clean
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed"

test:
	$(PYTHON) run_tests.py
	@echo "✓ Tests passed"

build: install test
	@echo "✓ Full build complete"

run:
	$(PYTHON) app.py
	@echo "✓ App started"

docker-build:
	docker build -t mathpuzzle:latest .
	@echo "✓ Docker image built: mathpuzzle:latest"

lint:
	@echo "Linting with flake8..."
	$(PIP) install flake8 2>/dev/null || true
	$(PYTHON) -m flake8 --max-line-length=120 src/ mathpuzzle_app/ app.py || true
	@echo "✓ Linting complete"

format:
	@echo "Formatting with black..."
	$(PIP) install black 2>/dev/null || true
	$(PYTHON) -m black src/ mathpuzzle_app/ app.py --line-length=120
	@echo "✓ Formatting complete"

.DEFAULT_GOAL := help
