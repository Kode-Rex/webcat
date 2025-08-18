# WebCat MCP Server - Development Makefile
.PHONY: help install install-dev format lint test test-coverage clean build docker-build docker-run demo health check-all pre-commit setup-dev

# Default target
help: ## Show this help message
	@echo "WebCat MCP Server - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
setup-dev: ## Set up development environment with all tools
	@echo "🔧 Setting up development environment..."
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/pre-commit install
	@echo "✅ Development environment ready!"

install: ## Install production dependencies
	@echo "📦 Installing production dependencies..."
	pip install -r docker/requirements.txt

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt
	pre-commit install

# Code quality
format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	black --config pyproject.toml .
	isort --settings-path pyproject.toml .
	@echo "✅ Code formatted!"

format-check: ## Check code formatting without making changes
	@echo "🔍 Checking code format..."
	black --config pyproject.toml --check --diff .
	isort --settings-path pyproject.toml --check-only --diff .

lint: ## Run essential linting checks (matches CI)
	@echo "🔍 Running linting checks..."
	python -m flake8 --version
	flake8 .
	@echo "✅ Linting complete!"

lint-full: ## Run all linting checks (including MyPy and Bandit)
	@echo "🔍 Running full linting checks..."
	python -m flake8 --version
	python -m flake8 . || echo "⚠️ Flake8 had issues, continuing..."
	mypy --config-file pyproject.toml . || echo "⚠️ MyPy had issues, continuing..."
	bandit -r . -f json -o bandit-report.json || echo "⚠️ Bandit had issues, continuing..."
	@echo "✅ All linting checks attempted!"

lint-fix: ## Fix auto-fixable linting issues
	@echo "🔧 Fixing linting issues..."
	autopep8 --in-place --recursive --aggressive --aggressive .
	autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables .

# Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	cd docker && python -m pytest tests/ -v

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	cd docker && python -m pytest tests/ -v --cov=. --cov-report=xml --cov-report=html --cov-report=term

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	cd docker && python -m pytest . -v -k integration --tb=short

# Quality checks
check-all: format-check lint test ## Run all quality checks (CI pipeline)
	@echo "✅ All quality checks passed!"

check-all-full: format-check lint-full test ## Run all quality checks including strict linting
	@echo "✅ All quality checks completed!"

docker-lint: ## Lint Dockerfiles (requires Docker running)
	@echo "🐳 Linting Dockerfiles..."
	@if command -v hadolint >/dev/null 2>&1; then \
		hadolint docker/Dockerfile; \
	else \
		echo "⚠️ hadolint not installed. Install with: brew install hadolint"; \
	fi

security: ## Run security checks
	@echo "🔒 Running security checks..."
	bandit -r . -f json -o bandit-report.json
	safety check --json --output safety-report.json || true
	@echo "✅ Security checks complete!"

security-check: security ## Alias for security target (CI compatibility)

audit: ## Run dependency audit
	@echo "🔍 Running dependency audit..."
	pip-audit --format=json --output=audit-report.json || true
	@echo "✅ Dependency audit complete!"

# Docker operations
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	cd docker && ./build.sh

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 -p 8001:8001 -e WEBCAT_MODE=demo webcat:latest

docker-run-prod: ## Run Docker container in production mode
	@echo "🐳 Running Docker container in production mode..."
	docker run -p 8000:8000 -e WEBCAT_MODE=mcp webcat:latest

# Development servers
demo: ## Start demo server locally
	@echo "🎨 Starting demo server..."
	cd docker && source venv/bin/activate && python cli.py --mode demo --port 8000

demo-bg: ## Start demo server in background
	@echo "🎨 Starting demo server in background..."
	cd docker && source venv/bin/activate && nohup python cli.py --mode demo --port 8000 > demo.log 2>&1 &
	@echo "Demo server started in background. Check demo.log for logs."

mcp: ## Start MCP server locally
	@echo "🛠️ Starting MCP server..."
	cd docker && source venv/bin/activate && python cli.py --mode mcp --port 8000

stop-bg: ## Stop background servers
	@echo "🛑 Stopping background servers..."
	pkill -f "python cli.py" || true
	pkill -f "python simple_demo.py" || true
	@echo "Background servers stopped."

# Health and monitoring
health: ## Check server health
	@echo "💗 Checking server health..."
	curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8001/health | jq .

status: ## Check server status
	@echo "📊 Checking server status..."
	curl -s http://localhost:8000/status | jq . || curl -s http://localhost:8001/status | jq .

logs: ## Show recent logs
	@echo "📝 Recent logs..."
	tail -f docker/demo.log || tail -f /tmp/webcat*.log

# Cleanup
clean: ## Clean up temporary files and caches
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	find . -type f -name ".coverage" -delete || true
	find . -type d -name "htmlcov" -exec rm -rf {} + || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + || true
	rm -f bandit-report.json safety-report.json || true
	@echo "✅ Cleanup complete!"

clean-all: clean ## Clean everything including venv
	@echo "🧹 Deep cleaning..."
	rm -rf venv/ || true
	rm -rf docker/venv/ || true
	@echo "✅ Deep cleanup complete!"

# Build and release
build: clean format lint test ## Build the project
	@echo "🏗️ Building project..."
	python -m build
	@echo "✅ Build complete!"

# Pre-commit hooks
pre-commit: ## Run pre-commit hooks on all files
	@echo "🔍 Running pre-commit hooks..."
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "⬆️ Updating pre-commit hooks..."
	pre-commit autoupdate

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	cd docs && make html || echo "No docs directory found"

# Environment info
env-info: ## Show environment information
	@echo "🔍 Environment Information"
	@echo "========================="
	@echo "Python: $(shell python --version)"
	@echo "pip: $(shell pip --version)"
	@echo "Working directory: $(shell pwd)"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Git commit: $(shell git rev-parse --short HEAD 2>/dev/null || echo 'Not a git repo')"

# Quick development workflow
dev: setup-dev format lint test demo ## Complete development setup and start demo
	@echo "🎉 Development environment ready and demo server running!"

# CI simulation
ci: ## Simulate CI pipeline locally
	@echo "🤖 Simulating CI pipeline..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test-coverage
	@echo "✅ CI simulation complete!"
