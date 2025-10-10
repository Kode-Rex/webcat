# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WebCat is a **Model Context Protocol (MCP) server** that provides web search and content extraction capabilities for AI models. The system is built with **FastMCP** and offers:

1. **Web Search Tool**: Search the web using Serper API or DuckDuckGo fallback
2. **Content Extraction**: Full webpage scraping with markdown conversion using Readability
3. **MCP Compliance**: SSE transport for compatibility with Claude Desktop and LiteLLM

**Tech Stack**: Python, FastAPI, FastMCP, BeautifulSoup, Readability, html2text, Serper/DuckDuckGo

## Architecture

### High-Level Flow

```
MCP Client → FastMCP Server (SSE) → Search Tool Decision
│
├─ Serper API (premium): Google-powered search with better ranking
│
└─ DuckDuckGo (free): Automatic fallback, no API key required
     │
     └─ Content Scraper (Readability + html2text) → Markdown Response
```

### Key Components

**MCP Server (Python/FastAPI)**:
- `docker/mcp_server.py` - FastMCP server with SSE transport
- `docker/health.py` - Health check and status endpoints
- `docker/demo_server.py` - Demo client interface
- `docker/api_tools.py` - Additional API tooling

**Core Modules**:
- `mcp_server.py:search_tool()` - Main search tool with automatic fallback
- `mcp_server.py:fetch_search_results()` - Serper API integration
- `mcp_server.py:fetch_duckduckgo_search_results()` - Free fallback search
- `mcp_server.py:scrape_search_result()` - Content extraction and markdown conversion
- `mcp_server.py:process_search_results()` - Result processing pipeline

**Azure Functions (Legacy)**:
- `customgpt/` - Azure Functions API for custom GPTs (separate deployment)

### MCP Tools

The server exposes **two MCP tools**:

1. **`search`**: Web search with automatic fallback
   - Takes query string parameter
   - Returns structured results with title, URL, snippet, and full content
   - Uses Serper API if `SERPER_API_KEY` configured, otherwise DuckDuckGo
   - Automatically scrapes and converts content to markdown

2. **`health_check`**: Server health status
   - Returns service health and status information

### Content Processing Pipeline

```python
Search Query → API Call (Serper/DuckDuckGo)
  → List of URLs
  → Parallel Scraping (requests + Readability)
  → HTML Extraction
  → Markdown Conversion (html2text)
  → Result Formatting with Citations
```

The scraper handles multiple content types (HTML, plain text, PDF detection) and includes fallback logic for failed extractions.

## Development Commands

### Running the Application

```bash
# Development mode with auto-reload (recommended for local dev)
make dev         # Start MCP server with auto-reload
make dev-demo    # Start demo server with auto-reload

# Quick start with Docker (recommended for testing)
docker run -p 8000:8000 tmfrisinger/webcat:latest

# With Serper API key for premium search
docker run -p 8000:8000 -e SERPER_API_KEY=your_key tmfrisinger/webcat:latest

# Build and run locally (multi-platform support)
cd docker
./build.sh  # Builds for linux/amd64 and linux/arm64
docker-compose up

# Build multi-platform and push to registry
cd docker
docker buildx build --platform linux/amd64,linux/arm64 \
  -t tmfrisinger/webcat:2.3.0 \
  -t tmfrisinger/webcat:latest \
  -f Dockerfile --push .

# Production mode (no auto-reload)
make mcp         # Start MCP server
make demo        # Start demo server

# First-time setup
make setup-dev   # Install all dependencies and setup pre-commit hooks

# Alternative: Install using pyproject.toml directly
pip install -e ".[dev]"     # Development dependencies
pip install -e ".[all]"     # All optional dependencies
```

**Ports and Endpoints**:
- **MCP Server**: http://localhost:8000/mcp
- **Demo Client**: http://localhost:8000/client
- **Health Check**: http://localhost:8000/health
- **Status**: http://localhost:8000/status

**Development mode features**:
- Auto-reload on file changes (watchdog)
- Detailed logging for debugging
- No need to restart server after code changes

### Testing

**Run all tests**:
```bash
# From docker/ directory
cd docker

# Run all tests (requires running MCP server for integration tests)
python -m pytest -v

# CI-safe tests only (no external dependencies)
python -m pytest -v -m "not integration"

# Unit tests only
python -m pytest -v -m "unit"

# Integration tests (requires running server on port 8000)
python -m pytest -v -m "integration"

# With coverage
python -m pytest --cov=mcp_server --cov-report=html --cov-report=term
```

**Run specific tests**:
```bash
# Test DuckDuckGo fallback functionality
python -m pytest test_duckduckgo_fallback.py -v -s

# Test MCP protocol directly (standalone)
python test_mcp_protocol.py

# Test search functions (unit tests)
python -m pytest tests/test_mcp_server.py -v
```

**Test requirements**:
- **Coverage**: 70% minimum for all metrics
- **Test markers**: Use `@pytest.mark.unit` for unit tests, `@pytest.mark.integration` for integration tests
- **Test isolation**: Tests should not depend on external services unless marked as integration tests

### Code Quality

```bash
# Format code (from project root)
make format         # Format all Python code with Black + isort
make format-check   # Check formatting without changes

# Lint code
make lint           # Run flake8 on all code
make lint-api       # Lint docker/ directory only

# Security checks
make security       # Run bandit security scanner
make audit          # Check dependencies for vulnerabilities

# Pre-commit hooks
make pre-commit-install  # Install git hooks
make pre-commit-run      # Run all pre-commit hooks manually

# CI simulation (run before pushing)
make ci             # Full CI: format-check + lint + test-coverage + security + audit
make ci-fast        # Fast CI: format-check + lint + test (no security/audit)
```

**Code formatting standards**:
- **Black**: line-length=88, target Python 3.11
- **isort**: profile="black" for import sorting
- **flake8**: E501 line length handled by Black
- **Pre-commit hooks**: Auto-format on commit

## Test Architecture

### Test Patterns

This codebase follows **pytest best practices** with clear test organization:

**✅ Good** - Use pytest markers and fixtures:
```python
@pytest.mark.unit
def test_content_scraping(mock_search_result):
    result = scrape_search_result(mock_search_result)
    assert result.content.startswith("# ")
```

**✅ Good** - Mock external dependencies:
```python
@pytest.mark.unit
@patch('mcp_server.requests.get')
def test_scraping_with_mock(mock_get):
    mock_get.return_value.text = "<html>...</html>"
    # Test logic here
```

**❌ Bad** - Tests that require external services without markers:
```python
def test_live_search():  # Missing @pytest.mark.integration
    result = fetch_duckduckgo_search_results("test")
```

### Test Structure

**MCP Server Tests** (`docker/tests/`):
- `test_mcp_server.py` - Unit tests for content processing, utilities
- `test_duckduckgo_fallback.py` - Integration tests for DuckDuckGo search
- `test_mcp_protocol.py` - Full MCP protocol integration tests
- `test_search_functions.py` - Unit tests for search logic
- `test_serper.py` - Serper API integration tests (requires API key)

**Test Organization**:
- **Unit tests**: Mock external dependencies, fast execution, CI-safe
- **Integration tests**: Require running services, marked with `@pytest.mark.integration`
- **API tests**: Test external APIs, marked with `@pytest.mark.api`

### Common Test Issues

1. **Integration test failures**: Ensure MCP server is running on port 8000 before running integration tests. Use `python -m pytest -m "not integration"` for CI.

2. **Coverage drops**: All Python files in `docker/` are included. Add tests rather than excluding files.

3. **Mock failures**: When mocking requests, ensure you patch at the right module level (`@patch('mcp_server.requests.get')` not `@patch('requests.get')`).

## Code Formatting Rules

- **Python**: Black (line-length=88), isort (profile="black")
- **Imports**: Absolute imports preferred (`from docker.mcp_server import ...`)
- **Type hints**: Required for all function signatures (enforced by mypy)
- **Docstrings**: Google-style docstrings for public functions

### Architecture Standards

**Maximum Nesting Depth**: 3 levels or less
- Functions with deeper nesting must be refactored
- Extract helper methods to reduce complexity
- Each helper method should represent a single concept
- Example violation: 6-level nesting in content_scraper.py (fixed by extracting 10 helper methods)

**One Class Per File**:
- Each file should contain exactly one class definition
- Applies to both production code and test infrastructure
- Example: Split `mock_ddgs.py` (3 classes) into 3 separate files

**Methods for Concepts**:
- Extract helper methods for each logical concept or operation
- Helper methods should have clear, single responsibilities
- Prefer multiple small methods over one large method
- Example: `_fetch_content()`, `_convert_to_markdown()`, `_truncate_if_needed()`

**No Raw Mocks**:
- Never use `MagicMock()` with property assignment (e.g., `mock.status_code = 200`)
- Create typed mock classes instead (e.g., `MockHttpResponse`, `MockSerperResponse`)
- Use factory pattern for creating pre-configured test doubles
- Use builder pattern with fluent API for test data (e.g., `a_search_result().with_title("X").build()`)

### Single Source of Truth

**Tool Versions** are defined in `pyproject.toml` under `[project.optional-dependencies.dev]`:
- Pre-commit hooks use `language: system` to reference locally installed tools
- CI pipeline installs via `pip install -e ".[dev]"` and runs the same tools
- No version mismatches between pre-commit and CI

**Tool Rules/Configuration**:
- **Black**: `[tool.black]` in `pyproject.toml`
- **isort**: `[tool.isort]` in `pyproject.toml`
- **mypy**: `[tool.mypy]` in `pyproject.toml`
- **pytest**: `[tool.pytest.ini_options]` in `pyproject.toml`
- **coverage**: `[tool.coverage.*]` in `pyproject.toml`
- **Flake8**: `[flake8]` in `setup.cfg` (flake8 doesn't natively support pyproject.toml)

All tools reference their respective config files via CLI args:
- Pre-commit: `black --config pyproject.toml`, `isort --settings-path pyproject.toml`
- Makefile: Same commands
- CI: Same commands

This ensures:
- ✅ Pre-commit hooks use the exact same tool versions as CI
- ✅ Pre-commit hooks use the exact same rules/config as CI
- ✅ Developers see identical linting results locally and in CI
- ✅ `make format-check lint` produces identical results to pre-commit hooks

### CI Workflow

**Before committing:**
```bash
make format        # Auto-fix formatting issues
make lint          # Check for linting issues
```

**Before pushing (recommended):**
```bash
make ci-fast       # Quick validation (~30 seconds)
# OR
make ci            # Full validation with security checks (~2-3 minutes)
```

**On git commit:**
- Pre-commit hooks run automatically (black, isort, autoflake, flake8)
- Uses same tools/config as `make format-check lint`

**On git push (GitHub Actions):**
- Quality job: `make format-check lint`
- Test job: `make test-coverage`
- Security job: `make security` (PRs only)
- Audit job: `make audit` (PRs only)

**Result:** If `make ci` passes locally, GitHub Actions CI will pass! ✨

## Configuration

### Dependency Management

WebCat uses **pyproject.toml** (PEP 621) for all dependency management:

```bash
# Install production dependencies
pip install -e .

# Install with development tools
pip install -e ".[dev]"

# Install with testing tools
pip install -e ".[test]"

# Install with documentation tools
pip install -e ".[docs]"

# Install everything
pip install -e ".[all]"
```

**Note**: All dependencies are defined in `pyproject.toml`. No `requirements.txt` files are used except for:
- `customgpt/requirements.txt` - Azure Functions deployment (separate component)

### Environment Variables

- `SERPER_API_KEY` - **Optional** - Serper API key for premium search (falls back to DuckDuckGo if not set)
- `PORT` - Port to run server on (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `LOG_DIR` - Log file directory (default: /tmp)
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds (default: 60)
- `RATE_LIMIT_MAX_REQUESTS` - Max requests per window (default: 10)

**Setup**:
```bash
# Create .env file in docker/ directory
cd docker
cp .env.example .env  # If exists, or create manually
echo "SERPER_API_KEY=your_key_here" >> .env  # Optional

# Or pass directly to Docker
docker run -p 8000:8000 -e SERPER_API_KEY=your_key tmfrisinger/webcat:latest
```

## Common Workflows

### Adding a New MCP Tool

1. Define tool function in `docker/mcp_server.py` with `@mcp_server.tool()` decorator:
```python
@mcp_server.tool(
    name="tool_name",
    description="Tool description for AI models"
)
async def tool_name(param: str, ctx=None):
    """Detailed docstring."""
    # Implementation
    return result
```

2. Add any helper functions below the tool definition
3. Create unit tests in `docker/tests/test_mcp_server.py`
4. Add integration tests if needed in separate file
5. Update `docker/README.md` with tool documentation

### Adding a New Search Source

1. Add fetching function in `docker/mcp_server.py`:
```python
def fetch_newsource_search_results(query: str) -> List[Dict[str, Any]]:
    # Implementation
    pass
```

2. Update `search_tool()` to include new fallback logic
3. Add corresponding tests in `docker/tests/`
4. Update environment variables in `.env.example` if API key needed
5. Document in README.md

### Debugging MCP Server

1. Check Docker logs: `docker logs <container_id> -f`
2. Check log files: `/var/log/webcat/webcat.log` (in container)
3. Enable DEBUG logging: `LOG_LEVEL=DEBUG`
4. Use demo client: http://localhost:8000/client for interactive testing
5. Run health check: `curl http://localhost:8000/health`
6. Test MCP protocol: `python docker/test_mcp_protocol.py`

## Important Notes

- **MCP Protocol**: Uses SSE (Server-Sent Events) transport for LiteLLM compatibility
- **No Authentication**: Simplified setup - no API keys required for basic functionality
- **Automatic Fallback**: Serper API → DuckDuckGo if no key or if Serper fails
- **Content Processing**: Readability + html2text for clean markdown conversion
- **Rate Limiting**: Default 10 requests per 60 seconds (configurable via env vars)
- **Test Isolation**: Use `@pytest.mark.integration` for tests requiring external services
- **Docker First**: All deployment via Docker, local Python only for development
- **Multi-Platform Docker**: Images support both linux/amd64 and linux/arm64 architectures
- **Coverage Threshold**: 70% minimum enforced in CI
- **Python Version**: Requires Python 3.11 exactly (not 3.10 or 3.12)

## Docker Multi-Platform Builds

WebCat Docker images support multiple architectures for broad compatibility:

### Supported Platforms
- **linux/amd64**: Intel/AMD x86_64 processors (standard servers, Intel Macs)
- **linux/arm64**: ARM64 processors (Apple Silicon, AWS Graviton, Raspberry Pi)

### Local Multi-Platform Build
The `docker/build.sh` script automatically builds for both platforms using Docker buildx:

```bash
cd docker
./build.sh  # Builds for linux/amd64 and linux/arm64
```

### Manual Multi-Platform Build and Push
To build and push multi-platform images manually:

```bash
# Ensure buildx is available
docker buildx version

# Build and push to registry
docker buildx build --platform linux/amd64,linux/arm64 \
  -t tmfrisinger/webcat:2.3.0 \
  -t tmfrisinger/webcat:latest \
  -f docker/Dockerfile --push .
```

### Automated GitHub Actions Workflow
The `.github/workflows/docker-publish.yml` workflow automates multi-platform builds:

**Trigger on version tags:**
```bash
git tag v2.4.0
git push origin v2.4.0
```

**Manual trigger:**
- Go to Actions → "Build and Push Multi-Platform Docker Image"
- Click "Run workflow"
- Enter version (e.g., "2.4.0")

The workflow:
- Builds for linux/amd64 and linux/arm64
- Tags with semantic versioning (2.4.0, 2.4, latest)
- Pushes to Docker Hub automatically
- Includes build caching for faster builds

### Verifying Multi-Platform Support
Check that an image supports multiple platforms:

```bash
docker buildx imagetools inspect tmfrisinger/webcat:latest
# Should show manifests for linux/amd64 and linux/arm64
```

## Engineering Principles

### Testing Philosophy

**Organize by Concept, Not Structure**

Tests should mirror what you're verifying, not the file system. Group related behaviors together:
- Group tests by feature area or user journey, not by implementation file
- Use class-based test organization to cluster related scenarios
- Name tests to describe behavior: `test_rejects_invalid_email` not `test_validation_method_1`

**The Builder-Factory Pattern**

Separate test data creation from test logic:
- **Builders**: Create domain objects with fluent interfaces (`a_user().with_email("...").build()`)
- **Factories**: Create test doubles (mocks, stubs) with pre-configured behavior
- Pass configuration to factories at creation time, never mutate after construction
- This pattern eliminates brittle test setup and makes tests self-documenting

**Avoid Fixture Overuse**

Fixtures create hidden dependencies and coupling:
- Only use fixtures for truly shared, complex setup (like database connections)
- Prefer direct builder/factory calls in tests for clarity
- If you find yourself wrapping a factory in a fixture, remove the fixture

**Coverage as a Conversation Starter**

Coverage metrics tell you what code is executed, not what behaviors are verified:
- 70% minimum is a floor, not a ceiling
- Missing coverage often reveals untested edge cases or dead code
- 100% coverage doesn't mean bug-free; it means your tests ran all lines at least once
- Focus on testing critical paths thoroughly over hitting arbitrary numbers

### Observability and Tracing

**Visibility Before Debugging**

Every system behavior should be observable without code changes:
- Instrument decision points: what path did the system take and why?
- Capture inputs and outputs at boundaries (API calls, tool executions, agent decisions)
- Track latency at each stage to identify bottlenecks
- Log errors with enough context to understand what the system was attempting

**Structured Over Unstructured**

Logs should be queryable, not just readable:
- Use structured formats that machines can parse and aggregate
- Include correlation IDs to trace requests across services
- Tag events with dimensions (user_id, session_id, decision_type) for filtering
- Avoid logging sensitive data; use redaction if necessary

**Trace Complete User Journeys**

A single user action often triggers multiple system operations:
- Connect related events with trace IDs so you can follow the full story
- Capture timing data to understand where time is spent
- Show state transitions to understand how data changes through the pipeline
- Make traces accessible to engineers without database access

**Health Checks and Readiness**

Systems should self-report their health:
- Distinguish between "alive" (process is running) and "ready" (can handle traffic)
- Check dependencies in health endpoints (can we reach the database? the API?)
- Make health checks lightweight; they'll be called frequently
- Use health data to automatically route traffic away from degraded instances

### Security

**Defense in Depth**

Never rely on a single security control:
- Validate input at every boundary (UI, API, database)
- Assume every external input is malicious until proven otherwise
- Use allowlists (known good) over denylists (known bad) when possible
- Apply the principle of least privilege: grant minimum necessary permissions

**Secrets Management**

Credentials should never live in code:
- Use environment variables or secret management services
- Rotate secrets regularly; treat rotation as a normal operation
- Never log secrets, even in debug mode
- Use different credentials for different environments

**Authentication vs Authorization**

Know who they are (authentication) and what they can do (authorization):
- Verify identity before granting access (don't trust client-supplied identity)
- Check permissions at the resource level, not just the endpoint level
- Default to deny; require explicit grants
- Audit authorization failures to detect attack attempts

**Network Security**

Control what can communicate with what:
- Restrict cross-origin requests to known clients
- Use encryption in transit (TLS) for all external communication
- Validate all external inputs before processing
- Rate limit to prevent abuse and resource exhaustion

**Update Dependencies Regularly**

Today's secure library is tomorrow's vulnerability:
- Monitor for security advisories in your dependencies
- Update promptly when vulnerabilities are disclosed
- Pin versions to avoid surprise breaking changes
- Balance stability with security; sometimes you must take the update

### Code Organization

**Single Concept Per File**

Each file should answer one question:
- **Models**: What data structures exist? (`user.py`, `chat_message.py`)
- **Services**: What business operations can we perform? (`vector_store.py`, `document_processor_service.py`)
- **Configuration**: How is the system configured? (`config.py`)
- **Tools**: What capabilities do we expose? (`tools.py`)

This makes files findable: need the User model? Look in `user.py`, not `models/business/entities/user.py`.

**Avoid Deep Nesting**

Depth creates navigation burden:
- Prefer flat structures: `services/email_service.py` over `services/communication/email/email_service.py`
- If you need categories, use one level: `models/user.py`, `models/message.py`
- Deep nesting often signals missing abstractions or overly complex organization
- Exception: group tests by concept (`tests/services/`, `tests/models/`) to separate test code from production code

**Co-locate Related Concerns**

Files that change together should live together:
- Put all chat-related models in `models/` (message, request, response)
- Put all agent-related logic in one place (`agent.py`)
- Don't scatter a feature across distant directories
- If you're frequently jumping between files, consider merging them

**Explicit Over Implicit**

Code should reveal intent:
- Use descriptive names: `retry_with_exponential_backoff()` not `retry()`
- Make dependencies explicit through imports and type hints
- Avoid magic: globals, implicit side effects, hidden state
- Configuration should be declarative and centralized, not scattered

**Small, Focused Modules**

A file should fit in your head:
- If a file is hard to navigate, split it by responsibility
- Each module should have a clear purpose expressible in one sentence
- Large files often mean multiple concepts bundled together
- Size isn't the only metric; a 500-line file with one concept is fine

## Documentation

- **Main README**: `README.md` - Quick start, features, and Docker usage
- **MCP Server README**: `docker/README.md` - Detailed MCP server documentation, testing guide
- **Examples**: `examples/` - Example usage and integration patterns
- **Assets**: `assets/` - Demo screenshots and visual documentation
- **CustomGPT**: `customgpt/` - Azure Functions API documentation (legacy)
