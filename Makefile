# Makefile for LLM Code Deployment System

.PHONY: help setup install test run clean docker-build docker-run round1 round2 evaluate

# Default target
help:
	@echo "LLM Code Deployment System - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Run initial setup (venv + install)"
	@echo "  make install        - Install dependencies"
	@echo "  make playwright     - Install Playwright browsers"
	@echo ""
	@echo "Running:"
	@echo "  make run            - Start the application"
	@echo "  make test           - Run test suite"
	@echo "  make dashboard      - Open dashboard in browser"
	@echo ""
	@echo "Instructor Tasks:"
	@echo "  make round1         - Send Round 1 tasks"
	@echo "  make round2         - Send Round 2 tasks"
	@echo "  make evaluate       - Run evaluation"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make docker-stop    - Stop Docker container"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean up generated files"
	@echo "  make logs           - Show application logs"
	@echo ""

# Setup
setup:
	@echo "Setting up LLM Code Deployment System..."
	chmod +x setup.sh
	./setup.sh

# Install dependencies
install:
	pip install -r requirements.txt

# Install Playwright
playwright:
	playwright install chromium

# Run application
run:
	python app.py

# Run tests
test:
	python test_system.py

# Open dashboard
dashboard:
	@echo "Opening dashboard..."
	@python -c "import webbrowser; webbrowser.open('http://localhost:7860/dashboard')"

# Send Round 1 tasks
round1:
	@if [ ! -f submissions.csv ]; then \
		echo "Error: submissions.csv not found"; \
		echo "Create it from submissions.csv.example"; \
		exit 1; \
	fi
	python scripts/round1.py submissions.csv

# Send Round 2 tasks
round2:
	python scripts/round2.py

# Run evaluation
evaluate:
	python scripts/evaluate.py

# Docker build
docker-build:
	docker build -t llm-deployment .

# Docker run
docker-run:
	docker run -p 7860:7860 \
		--env-file config/.env \
		--name llm-deployment \
		llm-deployment

# Docker stop
docker-stop:
	docker stop llm-deployment
	docker rm llm-deployment

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✓ Cleanup complete"

# Show logs
logs:
	@if [ -d logs ]; then \
		tail -f logs/*.log; \
	else \
		echo "No logs directory found"; \
	fi

# Database init
db-init:
	python -c "from database.db import init_db; init_db(); print('✓ Database initialized')"

# Database reset
db-reset:
	@echo "⚠️  This will delete all data. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	rm -f data/*.db
	python -c "from database.db import init_db; init_db(); print('✓ Database reset')"

# Check configuration
check-config:
	@echo "Checking configuration..."
	@python -c "from config.config import config; config.validate(); print('✓ Configuration valid')"

# Format code
format:
	black api/ database/ scripts/ utils/ templates/ *.py

# Lint code
lint:
	pylint api/ database/ scripts/ utils/ templates/ --disable=C0111,R0903

# Export requirements
freeze:
	pip freeze > requirements.txt

# Development mode
dev:
	uvicorn app:app --reload --host 0.0.0.0 --port 7860

# Production mode
prod:
	gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860
