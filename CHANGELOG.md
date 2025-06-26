# Changelog

All notable changes to the Ophelos Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2024-06-24

### Added
- **Access Token Authentication**: Added support for direct access token authentication alongside OAuth2
  - New `StaticTokenAuthenticator` class for pre-provided tokens
  - Enhanced `OphelosClient` with optional `access_token` parameter
  - Smart authentication selection (either access_token or OAuth2 credentials required)
- **Model-First API Approach**: Enhanced all models with `to_api_body()` method for intelligent field management
  - Smart server field exclusion (id, object, created_at, updated_at automatically filtered)
  - Intelligent relationship handling (customer/organisation → ID references, others → full objects)
  - Configurable field inclusion with `__api_body_fields__` class attributes
- **Comprehensive Test Coverage**: Added 143 model tests and 254+ total tests
  - Complete coverage of all Pydantic models including API body generation
  - Field validation, enum handling, and relationship processing tests
  - Authentication tests for both OAuth2 and access token methods
  - Integration tests with graceful fallback for invalid API responses

### Enhanced
- **Model Organization**: Reorganized models from monolithic `models.py` into separate files
  - Individual model files: `customer.py`, `debt.py`, `payment.py`, `invoice.py`, etc.
  - Enhanced `models/__init__.py` with proper exports and model rebuilding
  - Better maintainability and clearer code organization
- **Error Handling**: Improved robustness with graceful fallback mechanisms
  - Invalid API responses now fall back to raw dictionaries when model parsing fails
  - Enhanced error messages with detailed response information
  - Better handling of JSON serialization for date/datetime objects
- **Code Quality**: Applied comprehensive formatting and linting
  - Black formatting with 120-character line length
  - isort import sorting across all Python files
  - mypy type checking compliance
  - flake8 style compliance

### Fixed
- **JSON Serialization**: Fixed `TypeError: Object of type date is not JSON serializable`
  - Added proper date/datetime handling in `_process_nested_value()` method
  - Date objects now convert to ISO format strings automatically
- **Type Safety**: Resolved mypy type annotation errors
  - Fixed `PaginatedResponse` type handling in `BaseResource`
  - Added explicit type annotations for parsed items lists
- **PaginatedResponse Handling**: Fixed `basic_usage.py` example errors
  - Corrected `len(all_debts)` to `len(all_debts.data)`
  - Fixed slicing operations on `PaginatedResponse` objects
- **Import Organization**: Standardized import sorting across entire codebase
  - 60 files updated with consistent import organization
  - Standard library, third-party, and local imports properly separated

### Technical
- **Smart Field Management**: Implemented intelligent API body generation
  - Automatic exclusion of server-generated fields
  - Relationship field conversion (objects → IDs where appropriate)
  - Nested object processing with proper serialization
- **Authentication Flexibility**: Dual authentication support
  - OAuth2 client credentials flow (existing)
  - Direct access token authentication (new)
  - Environment variable support for both methods
- **Development Tools**: Enhanced development experience
  - Updated Black, isort, and flake8 configurations for 120-character lines
  - Added autoflake for removing unused imports and variables
  - Comprehensive test suite with model-specific test files
  - Better error handling examples and documentation

## [1.0.2] - 2024-06-14

### Added
- **Multi-tenant support**: Added `tenant_id` parameter to `OphelosClient` constructor
- **Thread-safe authentication**: Implemented thread-safe OAuth2 token management with `threading.RLock()`
- **Concurrent usage examples**: Added comprehensive examples for using the SDK with `ThreadPoolExecutor`
- **Thread safety tests**: Added dedicated test suite for concurrent usage patterns
- **Complete configuration reference**: Enhanced documentation with all client parameters

### Enhanced
- **Authentication**: OAuth2 authenticator now uses thread-safe token caching for concurrent requests
- **HTTP Client**: Automatic `OPHELOS_TENANT_ID` header injection when `tenant_id` is specified
- **Documentation**: Updated README.md and USAGE.md with multi-tenant usage patterns
- **Test coverage**: Added 5 new thread safety tests covering concurrent token access and refresh
- **Error handling**: Improved type safety with proper type casting in authentication flow

### Fixed
- **Code cleanup**: Removed obvious and redundant comments throughout the codebase
- **Type safety**: Fixed mypy type errors in authentication module
- **Code formatting**: Applied black formatting to all Python files for consistency

### Technical
- **Jittered retry**: Enhanced retry logic with additive jitter (0-1.5s) to prevent thundering herd
- **Performance**: Optimized authentication for high-concurrency scenarios
- **Memory efficiency**: Shared authentication tokens across concurrent threads

## [1.0.0] - 2024-01-15

### Added
- Initial release of the Ophelos Python SDK
- Complete API coverage for Ophelos API v20250401
- OAuth2 client credentials authentication
- Type-safe models using Pydantic
- Comprehensive error handling with custom exceptions
- Resource managers for all API endpoints:
  - Debts management (create, update, list, search, lifecycle operations)
  - Customer management (create, update, list, search)
  - Organisation management
  - Payment management (create, list, search)
  - Invoice management
  - Payment plan management
  - Communication management
  - Webhook management
  - Payout management
  - Tenant management
- Webhook signature validation and event parsing
- Built-in pagination support
- Search functionality with query language support
- Automatic token refresh and retry logic
- Expandable response fields support
- Comprehensive documentation and examples
- Type hints and mypy support
- Modern Python packaging with pyproject.toml

### Security
- HMAC-SHA256 webhook signature verification
- Secure credential handling
- Automatic token expiration and refresh

### Documentation
- Complete API reference documentation
- Usage examples and best practices
- Webhook handling examples
- Authentication setup guide

## [Unreleased]

### Fixed
- **Pagination Issue**: Fixed `has_more` always returning `False` in paginated responses
  - Updated HTTP client to extract pagination information from response headers per [Ophelos API specification](https://ophelos-api.readme.io/reference/pagination)
  - Added parsing of `Link` header to determine if more pages are available (`rel="next"`)
  - Added extraction of `X-Total-Count` header for total count information
  - Enhanced `_handle_response()` method to detect list responses and process pagination headers
  - **Enhanced Link Header Parsing**: Extract cursor values (`after`, `before`) from `next`, `prev`, and `first` relations
  - Added `pagination` field to `PaginatedResponse` with easy-to-use cursor navigation
  - Added comprehensive tests for header-based pagination scenarios including Link header parsing

### Changed
- **BREAKING CHANGE**: Package renamed from `ophelos` to `ophelos_sdk` for better namespace management
- Import statements now use `from ophelos_sdk import OphelosClient` instead of `from ophelos import OphelosClient`
- All module imports updated to use `ophelos_sdk.*` namespace

### Planned
- Async client support
- Enhanced error messages with suggestion
- CLI tool for API testing
- Additional utility functions
- Performance optimizations 