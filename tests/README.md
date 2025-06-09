# Ophelos SDK Tests

This directory contains comprehensive tests for the Ophelos Python SDK.

## Test Structure

### Unit Tests

- **`test_models.py`** - Tests for Pydantic models (Debt, Customer, Payment, etc.)
- **`test_auth.py`** - Tests for OAuth2 authentication functionality
- **`test_http_client.py`** - Tests for HTTP client with error handling and retries
- **`test_webhooks.py`** - Tests for webhook signature validation and parsing
- **`test_resources.py`** - Tests for API resource managers (debts, customers, payments, etc.)

### Integration Tests

- **`test_integration.py`** - Integration tests that require valid API credentials

### Test Configuration

- **`conftest.py`** - Shared fixtures and test configuration
- **`pytest.ini`** - Pytest configuration with coverage settings

## Running Tests

### Quick Start

```bash
# Run all unit tests (default)
python -m pytest

# Run tests with coverage
python -m pytest --cov=ophelos

# Run only specific test file
python -m pytest tests/test_models.py -v
```

### Using the Test Runner Script

```bash
# Run unit tests only (default)
python scripts/run_tests.py

# Run with verbose output
python scripts/run_tests.py --verbose

# Run fast without coverage
python scripts/run_tests.py --fast

# Run integration tests (requires credentials)
python scripts/run_tests.py --integration

# Run all tests including integration
python scripts/run_tests.py --all
```

## Integration Tests

Integration tests require valid Ophelos API credentials. Set these environment variables:

```bash
export OPHELOS_CLIENT_ID="your_client_id"
export OPHELOS_CLIENT_SECRET="your_client_secret"
export OPHELOS_AUDIENCE="your_audience"
```

Integration tests will be skipped if credentials are not provided.

## Test Coverage

The test suite aims for high coverage across all modules:

- **Models**: 100% - All Pydantic models and enums
- **Authentication**: 100% - OAuth2 flow with token management
- **HTTP Client**: 100% - Request handling and error management
- **Webhooks**: 100% - Signature validation and event parsing
- **Resources**: 85%+ - API resource managers and operations

## Test Data

Tests use mock data and fixtures defined in `conftest.py`. This includes:

- Sample debt, customer, and payment data
- Mock HTTP responses
- Webhook event examples
- Authentication token responses

## Best Practices

1. **Unit tests should be fast** - Use mocks for external dependencies
2. **Integration tests verify real API calls** - But use staging environment
3. **Test error conditions** - Verify proper exception handling
4. **Use descriptive test names** - Make failures easy to understand
5. **Keep tests isolated** - Each test should be independent

## Continuous Integration

The test suite is designed to run in CI environments:

- Unit tests run on every commit
- Integration tests can be enabled with proper credentials
- Coverage reports are generated automatically
- Tests are compatible with common CI platforms

## Adding New Tests

When adding new features:

1. Add unit tests for new models in `test_models.py`
2. Add resource tests in `test_resources.py`
3. Add integration tests in `test_integration.py` if needed
4. Update fixtures in `conftest.py` as required
5. Ensure coverage stays above 85% 