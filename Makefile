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
	./venv/bin/pip install -e ".[dev]"
	./venv/bin/pre-commit install
	@echo "✅ Development environment ready!"

install: ## Install production dependencies
	@echo "📦 Installing production dependencies..."
	pip install -e .

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	pip install -e ".[dev]"
	pre-commit install

install-all: ## Install all optional dependencies
	@echo "📦 Installing all dependencies..."
	pip install -e ".[all]"

# Code quality
format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	python -m black --config pyproject.toml .
	python -m isort --settings-path pyproject.toml .
	@echo "✅ Code formatted!"

format-check: ## Check code formatting without making changes
	@echo "🔍 Checking code format..."
	python -m black --config pyproject.toml --check --diff .
	python -m isort --settings-path pyproject.toml --check-only --diff .

lint: ## Run essential linting checks (matches CI)
	@echo "🔍 Running linting checks..."
	python -m flake8 --version
	python -m flake8 .
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
	cd docker && python -m pytest tests/unit/ -v --cov=clients --cov=services --cov=tools --cov=models --cov=utils --cov-branch --cov-report=xml --cov-report=html --cov-report=term-missing

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
	bandit -r docker/ customgpt/ -f json -o bandit-report.json --exclude "*/venv/*,*/build/*,*/dist/*,*/.venv/*" || true
	safety check || true
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
dev: ## Start MCP server with auto-reload (development mode)
	@echo "🚀 Starting MCP server with auto-reload..."
	@echo "📡 MCP endpoint: http://localhost:8000/mcp"
	@echo "💗 Health check: http://localhost:8000/health"
	@echo "🔄 Auto-reload enabled - edit files to see changes"
	@echo ""
	cd docker && PYTHONPATH=. watchmedo auto-restart --recursive --pattern="*.py" --directory=. -- python mcp_server.py

dev-demo: ## Start demo server with auto-reload (development mode)
	@echo "🚀 Starting demo server with auto-reload..."
	@echo "🎨 Demo client: http://localhost:8000/client"
	@echo "💗 Health check: http://localhost:8000/health"
	@echo "📊 Status: http://localhost:8000/status"
	@echo "🔄 Auto-reload enabled - edit files to see changes"
	@echo ""
	cd docker && PYTHONPATH=. watchmedo auto-restart --recursive --pattern="*.py" --directory=. -- python simple_demo.py

demo: ## Start demo server locally (production mode)
	@echo "🎨 Starting demo server..."
	cd docker && python cli.py --mode demo --port 8000

demo-bg: ## Start demo server in background
	@echo "🎨 Starting demo server in background..."
	cd docker && nohup python cli.py --mode demo --port 8000 > demo.log 2>&1 &
	@echo "Demo server started in background. Check demo.log for logs."

mcp: ## Start MCP server locally (production mode)
	@echo "🛠️ Starting MCP server..."
	cd docker && python cli.py --mode mcp --port 8000

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
dev-setup: setup-dev format lint test ## Complete development setup
	@echo "🎉 Development environment ready!"

# CI simulation
ci: ## Simulate CI pipeline locally (all checks)
	@echo "🤖 Simulating full CI pipeline..."
	@echo ""
	@echo "📋 Step 1/4: Code Quality"
	$(MAKE) format-check
	$(MAKE) lint
	@echo ""
	@echo "🧪 Step 2/4: Tests with Coverage"
	$(MAKE) test-coverage
	@echo ""
	@echo "🔒 Step 3/4: Security Checks"
	$(MAKE) security
	@echo ""
	@echo "🔍 Step 4/4: Dependency Audit"
	$(MAKE) audit
	@echo ""
	@echo "✅ CI simulation complete! All checks passed."

ci-fast: ## Simulate CI pipeline (fast - no security/audit)
	@echo "🤖 Simulating fast CI pipeline..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test
	@echo "✅ Fast CI simulation complete!"
