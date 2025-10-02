# WebCat Testing Guide

This document explains the testing patterns, builders, and factories used in the WebCat project.

## Table of Contents
- [Test Structure](#test-structure)
- [Builder Pattern](#builder-pattern)
- [Factory Pattern](#factory-pattern)
- [Running Tests](#running-tests)
- [Coverage](#coverage)

---

## Test Structure

Tests are organized to mirror the production code structure:

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── builders/                # Fluent builders for test data
│   └── search_result_builder.py
├── factories/               # Factories for creating test doubles
│   └── http_factories.py
├── unit/                    # Unit tests (fast, no external dependencies)
│   ├── models/
│   ├── clients/
│   ├── services/
│   │   └── test_content_scraper.py
│   ├── tools/
│   └── utils/
└── integration/             # Integration tests (may call external services)
    └── test_duckduckgo_integration.py
```

### Test Organization Principles

1. **Mirror production structure** - Tests under `unit/services/` test code in `services/`
2. **Group by concept** - Use test classes to group related tests
3. **Descriptive names** - Test names describe behavior, not implementation

**Good example:**
```python
class TestContentScraperErrors:
    def test_returns_error_when_url_missing(self):
        # ...
```

**Bad example:**
```python
def test_scrape_function():  # ❌ What does this test?
    # ...
```

---

## Builder Pattern

Builders provide a fluent interface for creating test objects with sensible defaults.

### Why Use Builders?

- **Default valid state** - Every builder starts with a valid object
- **Fluent API** - Chain method calls for readability
- **Maintainability** - Change the model, update one builder
- **Self-documenting** - Builder names explain what's being created

### Available Builders

#### SearchResultBuilder

```python
from tests.builders.search_result_builder import a_search_result, a_wikipedia_article

# Create with defaults
result = a_search_result().build()

# Customize specific fields
result = (a_search_result()
          .with_title("My Custom Title")
          .with_url("https://custom.com")
          .with_snippet("Custom snippet")
          .build())

# Pre-configured builders
wiki_result = a_wikipedia_article().build()

# With markdown content
result = a_search_result().with_markdown_content().build()
```

### Creating New Builders

When you need a builder for a new model:

1. Create a new file in `tests/builders/`
2. Implement the builder class with fluent methods
3. Provide a helper function (e.g., `a_model_name()`)
4. Add pre-configured builders for common scenarios

**Template:**
```python
class MyModelBuilder:
    def __init__(self):
        self._field1 = "default_value"
        self._field2 = "default_value"

    def with_field1(self, value: str) -> "MyModelBuilder":
        self._field1 = value
        return self

    def with_field2(self, value: str) -> "MyModelBuilder":
        self._field2 = value
        return self

    def build(self) -> MyModel:
        return MyModel(field1=self._field1, field2=self._field2)

def a_my_model() -> MyModelBuilder:
    return MyModelBuilder()
```

---

## Factory Pattern

Factories create **typed test doubles**, not raw MagicMock objects with property assignment.

### Why Use Typed Test Doubles?

- **No raw mock property assignment** - Avoid `mock.status_code = 200` anti-pattern
- **Type safety** - Factories return properly typed test doubles
- **Immutable configuration** - All properties set via constructor
- **Eliminate duplication** - Mock configuration in one place
- **Consistent behavior** - All tests use same test double structure
- **Easy to modify** - Change behavior globally

### Available Factories

#### HttpResponseFactory

Returns `MockHttpResponse` instances (typed test doubles), not `MagicMock`.

```python
from tests.factories.http_response_factory import HttpResponseFactory

# Successful HTML response
mock_response = HttpResponseFactory.success()

# HTML with specific title
mock_response = HttpResponseFactory.html_with_title("Article Title")

# Plaintext response
mock_response = HttpResponseFactory.plaintext("Text content")

# PDF response
mock_response = HttpResponseFactory.pdf()

# Error responses
mock_response = HttpResponseFactory.error_404()
mock_response = HttpResponseFactory.error_500()

# Exceptions for side_effect
timeout_exception = HttpResponseFactory.timeout()
connection_exception = HttpResponseFactory.connection_error()
```

### Using Factories in Tests

```python
@patch("services.content_scraper.requests.get")
def test_scraper_handles_html(mock_get):
    # Arrange
    mock_get.return_value = HttpResponseFactory.html_with_title("Test")
    result = a_search_result().build()

    # Act
    scraped = scrape_search_result(result)

    # Assert
    assert "# Test" in scraped.content
```

### Creating New Factories

When you need a factory for new test doubles:

1. **Create a typed test double** in `tests/factories/mock_*.py`
2. **Create a factory** in `tests/factories/*_factory.py`
3. **Return typed test doubles**, not MagicMock with property assignment

**Step 1: Create Typed Test Double**
```python
# tests/factories/mock_api_response.py
class MockApiResponse:
    """Typed test double for API responses."""

    def __init__(self, status: str = "success", data: dict = None):
        self.status = status
        self.data = data or {}

    def json(self) -> dict:
        return {"status": self.status, "data": self.data}
```

**Step 2: Create Factory**
```python
# tests/factories/api_response_factory.py
from tests.factories.mock_api_response import MockApiResponse

class ApiResponseFactory:
    @staticmethod
    def successful_response(data: dict = None) -> MockApiResponse:
        return MockApiResponse(status="success", data=data or {"key": "value"})

    @staticmethod
    def error_response(error_code: int = 500) -> MockApiResponse:
        return MockApiResponse(
            status="error",
            data={"error_code": error_code, "message": "Error occurred"}
        )
```

**Why Typed Test Doubles?**

❌ **Bad: Raw MagicMock with property assignment**
```python
mock = MagicMock()
mock.status_code = 200  # Mutable, no type safety
mock.content = b"test"  # Can assign anything
mock.headers = {}       # Easy to forget properties
```

✅ **Good: Typed test double**
```python
class MockHttpResponse:
    def __init__(self, status_code: int, content: bytes, headers: dict):
        self.status_code = status_code  # Type-checked
        self.content = content           # Immutable after construction
        self.headers = headers           # All properties required
```

---

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit/
# or
pytest -m unit
```

### Run Integration Tests
```bash
pytest tests/integration/
# or
pytest -m integration
```

### Run Tests for Specific Module
```bash
pytest tests/unit/services/test_content_scraper.py
```

### Run Tests with Coverage
```bash
pytest --cov=services --cov-report=html
```

### Run Tests in Parallel
```bash
pytest -n auto  # Uses all CPU cores
```

### Run Specific Test Class
```bash
pytest tests/unit/services/test_content_scraper.py::TestContentScraperErrors
```

### Run Specific Test Method
```bash
pytest tests/unit/services/test_content_scraper.py::TestContentScraperErrors::test_returns_error_when_url_missing
```

---

## Coverage

### Target Coverage: 70%

We aim for at least 70% code coverage across all modules.

### Check Coverage
```bash
# Overall coverage
pytest --cov=. --cov-report=term

# Coverage for specific module
pytest tests/unit/services/ --cov=services --cov-report=term

# Generate HTML report
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View in browser
```

### Coverage Configuration

Coverage settings are in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["docker"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/venv/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

### Interpreting Coverage

- **Green (>70%)**: Good coverage
- **Yellow (50-70%)**: Needs improvement
- **Red (<50%)**: Insufficient coverage

Focus on:
1. **Critical paths** - Error handling, edge cases
2. **Business logic** - Services and tools
3. **Complex functions** - Functions with high cyclomatic complexity

Don't obsess over:
1. **Simple models** - Pydantic models are self-validating
2. **Constants** - No logic to test
3. **Entry points** - Tested via integration tests

---

## Fixtures

Shared fixtures are defined in `tests/conftest.py`:

### `configure_test_environment` (autouse)
Automatically configures environment variables and logging for all tests.

### `search_result_builder`
Provides a `SearchResultBuilder` instance.

### `wikipedia_result`
Provides a pre-built Wikipedia search result.

### `http_factory`
Provides an `HttpResponseFactory` instance.

### `mock_successful_http_get`
Automatically mocks `requests.get` with a successful response.

### `temp_test_dir`
Provides a temporary directory for file I/O tests.

---

## Best Practices

### 1. Use AAA Pattern (Arrange, Act, Assert)

```python
def test_example():
    # Arrange - Set up test data
    result = a_search_result().with_url("test").build()

    # Act - Execute the code under test
    scraped = scrape_search_result(result)

    # Assert - Verify expectations
    assert scraped.content.startswith("# ")
```

### 2. Group Related Tests in Classes

```python
class TestContentScraperErrors:
    """All error-handling tests for content scraper."""

    def test_handles_404(self):
        # ...

    def test_handles_timeout(self):
        # ...
```

### 3. Use Descriptive Test Names

Test names should answer: "What behavior am I verifying?"

**Good:**
- `test_returns_error_when_url_missing`
- `test_truncates_content_exceeding_max_length`
- `test_wraps_plaintext_in_code_blocks`

**Bad:**
- `test_scrape_function`
- `test_case_1`
- `test_error`

### 4. One Assertion Concept Per Test

Each test should verify one behavior. Multiple assertions are fine if they verify the same concept.

**Good:**
```python
def test_converts_html_to_markdown_with_metadata():
    # Verifying markdown conversion (one concept)
    assert content.startswith("# Title")
    assert "*Source: url*" in content
```

**Bad:**
```python
def test_everything():
    # Testing multiple unrelated concepts
    assert result.title == "Test"
    assert handle_error() raises Exception
    assert format_date() == "2024-01-01"
```

### 5. Don't Test Implementation Details

Test observable behavior, not internal implementation.

**Good:**
```python
def test_scraper_returns_markdown_content():
    result = scrape(url)
    assert result.content.startswith("#")  # Observable output
```

**Bad:**
```python
def test_scraper_calls_readability():
    with patch("scraper.Document") as mock:
        scrape(url)
        assert mock.called  # Testing internal call
```

---

## Troubleshooting

### Tests Not Found

If pytest can't find your tests:
```bash
# Check test discovery
pytest --collect-only

# Verify testpaths in pytest.ini
cat pytest.ini
```

### Import Errors

If imports fail:
```bash
# Ensure you're running pytest from docker/ directory
cd docker/
pytest

# Or use module mode
python -m pytest
```

### Fixture Not Found

If pytest says "fixture not found":
1. Check that `conftest.py` is in the right location
2. Ensure the fixture name matches exactly
3. Try running pytest with `-v` to see fixture discovery

---

## Adding New Tests

### Checklist for New Test Files

1. ✅ Place in correct directory (`unit/` or `integration/`)
2. ✅ Mirror production code structure
3. ✅ Import builders/factories from `tests.builders/factories`
4. ✅ Use fixtures from `conftest.py`
5. ✅ Group tests in classes by concept
6. ✅ Use descriptive test names
7. ✅ Follow AAA pattern
8. ✅ Add pytest markers if needed (`@pytest.mark.integration`)
9. ✅ Run coverage check
10. ✅ Verify tests pass in CI

---

## Questions?

If you have questions about testing patterns or need help writing tests:
1. Check this README
2. Look at existing tests in `tests/unit/services/test_content_scraper.py`
3. Ask in the team chat
