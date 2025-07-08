# Ophelos SDK Usage Guide

This guide shows comprehensive usage patterns for the Ophelos SDK, including advanced features like request/response transparency and model-first development.

## Installation

### Option 1: Install from Wheel (Recommended)

```bash
pip install dist/ophelos_sdk-1.4.0-py3-none-any.whl
```

### Option 2: Install from Source Distribution

```bash
pip install dist/ophelos-sdk-1.4.0.tar.gz
```

### Option 3: Development Installation

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"
```

## Error Handling & Debugging

The SDK provides comprehensive error handling with full request/response context for all error types:

- **API Errors** (`OphelosAPIError`): Include request details, response time, and status codes
- **Timeout Errors** (`TimeoutError`): Capture request context even when no response received
- **Parse Errors** (`ParseError`): Show request details when response parsing fails
- **Unexpected Errors** (`UnexpectedError`): Wrap any unexpected exceptions with request context

All exceptions provide the same debugging interface: `request_info`, `response_info`, and `response_raw` properties for complete transparency.

```python
try:
    debt = client.debts.get("invalid_id")
except OphelosAPIError as e:
    print(f"Request: {e.request_info['method']} {e.request_info['url']}")
    print(f"Response: {e.response_info['status_code']} in {e.response_raw.elapsed.total_seconds()}s")
except TimeoutError as e:
    print(f"Timeout after: {e.request_info}")  # Available even without response
```

## Authentication & Client Setup

### OAuth2 Authentication (Recommended)

```python
from ophelos_sdk import OphelosClient

# Production environment
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production",
    version="2025-04-01"
)

# Staging environment (default)
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    version="2025-04-01"
)

# Local development
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="development",  # Uses http://api.localhost:3000
    version="2024-12-01"
)
```

### Access Token Authentication

```python
# Direct access token
client = OphelosClient(
    access_token="your_access_token",
    environment="production",
    version="2025-04-01"
)
```

### Multi-Tenant Support

```python
# Single tenant client
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    tenant_id="tenant_123"  # Adds OPHELOS_TENANT_ID header to all requests
)

# Multiple tenant clients
clients = {
    "tenant_a": OphelosClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        audience="your_audience",
        tenant_id="tenant_a"
    ),
    "tenant_b": OphelosClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        audience="your_audience",
        tenant_id="tenant_b"
    )
}
```

## Request/Response Transparency

Every model instance returned by the SDK includes complete HTTP request and response information:

### Basic Request/Response Access

```python
# Get a customer
customer = client.customers.get('cust_123')

# Access request information
request_info = customer.request_info
print(f"Method: {request_info['method']}")           # GET
print(f"URL: {request_info['url']}")                 # https://api.ophelos.com/customers/cust_123
print(f"Headers: {request_info['headers']}")         # Auth headers, API version, etc.
print(f"Body: {request_info['body']}")               # None for GET requests

# Access response information
response_info = customer.response_info
print(f"Status: {response_info['status_code']}")     # 200
print(f"Headers: {response_info['headers']}")        # Content-Type, etc.
print(f"URL: {response_info['url']}")                # Final URL after redirects

# Access raw response object for advanced usage
raw_response = customer.response_raw
print(f"Response time: {raw_response.elapsed.total_seconds()} seconds")
print(f"Server: {raw_response.headers.get('Server')}")
print(f"Content length: {len(raw_response.content)} bytes")
```

### Request/Response with All Operations

```python
# Create operations include request details
new_customer = client.customers.create({
    "first_name": "John",
    "last_name": "Doe"
})

print(f"Creation request: {new_customer.request_info}")
# Shows POST method, request body, headers sent

# Update operations
updated_customer = client.customers.update("cust_123", {
    "preferred_locale": "en-GB"
})

print(f"Update request body: {updated_customer.request_info['body']}")
print(f"Update response time: {updated_customer.response_raw.elapsed}")

# List operations include request/response details
debts = client.debts.list(limit=10, expand=["customer"])

print(f"List request URL: {debts.request_info['url']}")
print(f"List response headers: {debts.response_info['headers']}")

# Individual items in lists also have request/response details
for debt in debts.data:
    print(f"Debt {debt.id} response time: {debt.response_raw.elapsed}")
```

### Advanced Request/Response Usage

```python
# Monitor API performance
def monitor_request_performance(operation_name, operation_func):
    """Monitor API request performance with detailed logging."""
    import time

    start_time = time.time()
    result = operation_func()
    end_time = time.time()

    # Get request/response details
    request_info = result.request_info
    response_info = result.response_info
    raw_response = result.response_raw

    print(f"=== {operation_name} Performance ===")
    print(f"Total time: {end_time - start_time:.3f}s")
    print(f"API response time: {raw_response.elapsed.total_seconds():.3f}s")
    print(f"Request URL: {request_info['url']}")
    print(f"Response status: {response_info['status_code']}")
    print(f"Response size: {len(raw_response.content)} bytes")

    return result

# Usage
debt = monitor_request_performance(
    "Get Debt with Expansions",
    lambda: client.debts.get("debt_123", expand=["customer", "payments"])
)

# Create audit trails
def audit_api_call(model_instance, operation_type):
    """Create audit trail for API operations."""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation_type": operation_type,
        "request": {
            "method": model_instance.request_info["method"],
            "url": model_instance.request_info["url"],
            "headers": {k: v for k, v in model_instance.request_info["headers"].items()
                       if k.lower() not in ["authorization"]},  # Exclude sensitive headers
            "body_size": len(str(model_instance.request_info["body"])) if model_instance.request_info["body"] else 0
        },
        "response": {
            "status_code": model_instance.response_info["status_code"],
            "response_time_ms": model_instance.response_raw.elapsed.total_seconds() * 1000,
            "content_length": len(model_instance.response_raw.content)
        }
    }

    # Log to your audit system
    print(f"Audit: {audit_entry}")
    return audit_entry

# Usage
customer = client.customers.create({"first_name": "John", "last_name": "Doe"})
audit_api_call(customer, "customer_creation")
```

## Model-First Development

### Understanding Model API Bodies

```python
from ophelos_sdk.models import Customer, Debt, Payment, ContactDetail

# Models automatically generate appropriate API request bodies
customer = Customer(
    id="temp_123",  # Temporary ID (excluded from API body)
    first_name="John",
    last_name="Doe",
    contact_details=[
        ContactDetail(
            id="temp_cd_1",  # Temporary ID (excluded from API body)
            type="email",
            value="john@example.com",
            primary=True
        )
    ],
    metadata={"source": "api"}
)

# Generate API body - only includes appropriate fields
api_body = customer.to_api_body()
print(api_body)
# Output: {
#   "first_name": "John",
#   "last_name": "Doe",
#   "contact_details": [
#     {"type": "email", "value": "john@example.com", "primary": True}
#   ],
#   "metadata": {"source": "api"}
# }

# Server-generated fields automatically excluded:
# - id, object, created_at, updated_at
assert "id" not in api_body
assert "object" not in api_body
assert "created_at" not in api_body
assert "updated_at" not in api_body

# Create using the model
created_customer = client.customers.create(customer)

# Access creation details
print(f"API sent: {created_customer.request_info['body']}")
print(f"Response time: {created_customer.response_raw.elapsed}")
```

### Smart Relationship Handling

```python
# Different relationship types handled intelligently
debt = Debt(
    id="temp_debt",
    customer="cust_123",  # String ID - preserved as-is
    organisation=existing_org_model,  # Model instance - becomes ID reference
    currency="GBP",
    account_number="ACC-001"
)

api_body = debt.to_api_body()
# customer: "cust_123" (string preserved)
# organisation: "org_456" (extracted from model.id)

# Nested objects remain as full objects
customer_with_contacts = Customer(
    id="temp_cust",
    first_name="Jane",
    contact_details=[
        ContactDetail(type="email", value="jane@example.com"),
        ContactDetail(type="phone", value="+44123456789")
    ]
)

api_body = customer_with_contacts.to_api_body()
# contact_details includes full objects (not ID references)
```

### Model Development Patterns

```python
# Pattern 1: Factory functions for complex models
def create_customer_with_full_contact_info(first_name, last_name, email, phone, address):
    """Factory to create comprehensive customer models."""
    contact_details = [
        ContactDetail(
            id=f"temp_email_{first_name.lower()}",
            type="email",
            value=email,
            primary=True,
            usage="billing"
        ),
        ContactDetail(
            id=f"temp_phone_{first_name.lower()}",
            type="phone",
            value=phone,
            usage="notifications"
        )
    ]

    if address:
        contact_details.append(
            ContactDetail(
                id=f"temp_address_{first_name.lower()}",
                type="address",
                value=address,
                usage="billing"
            )
        )

    return Customer(
        id=f"temp_cust_{first_name.lower()}_{last_name.lower()}",
        first_name=first_name,
        last_name=last_name,
        contact_details=contact_details,
        kind="individual",
        metadata={
            "created_via": "api_factory",
            "contact_count": len(contact_details)
        }
    )

# Usage with request/response monitoring
customer = create_customer_with_full_contact_info(
    "John", "Doe", "john@example.com", "+44123456789", "123 Main St"
)

print(f"Will send API body: {customer.to_api_body()}")

created_customer = client.customers.create(customer)

print(f"Customer created: {created_customer.id}")
print(f"Request details: {created_customer.request_info}")
print(f"Response time: {created_customer.response_raw.elapsed.total_seconds()}s")

# Pattern 2: Model validation and preview
def preview_and_create_debt(customer_id, org_id, amount_total, currency="GBP"):
    """Preview debt model before creation with validation."""
    debt = Debt(
        id="temp_debt_preview",
        customer=customer_id,
        organisation=org_id,
        currency=currency,
        total_amount=amount_total,
        account_number="ACC-PREVIEW",
        kind="purchased"
    )

    # Preview API body
    api_body = debt.to_api_body()
    print(f"Debt API body preview: {api_body}")

    # Validate required fields
    required_fields = ["customer", "organisation", "currency"]
    missing_fields = [field for field in required_fields if field not in api_body]

    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    # Create and return with request/response details
    created_debt = client.debts.create(debt)

    print(f"Debt created in: {created_debt.response_raw.elapsed.total_seconds()}s")
    print(f"Request URL: {created_debt.request_info['url']}")

    return created_debt

# Usage
debt = preview_and_create_debt("cust_123", "org_456", 100000)
```

## Working with Core Resources

### Debts Management

```python
from ophelos_sdk.models import Debt

# List debts with request/response monitoring
debts = client.debts.list(limit=50, expand=["customer", "organisation"])

print(f"List request took: {debts.response_raw.elapsed.total_seconds()}s")
print(f"Found {len(debts.data)} debts")

# Each debt has individual request/response details
for debt in debts.data:
    print(f"Debt {debt.id}: {debt.response_raw.status_code}")

# Search with performance monitoring
search_start = time.time()
results = client.debts.search("status:paying AND updated_at>=2024-01-01")
search_end = time.time()

print(f"Search total time: {search_end - search_start:.3f}s")
print(f"API response time: {results.response_raw.elapsed.total_seconds():.3f}s")
print(f"Search request: {results.request_info}")

# Create debt with model and monitor creation
debt_model = Debt(
    id="temp_new_debt",
    customer="cust_123",
    organisation="org_456",
    currency="GBP",
    account_number="ACC-2024-001",
    kind="purchased",
    metadata={"created_via": "sdk", "priority": "normal"}
)

# Preview before creation
print(f"Will send: {debt_model.to_api_body()}")

created_debt = client.debts.create(debt_model)

print(f"Created debt {created_debt.id}")
print(f"Creation request: {created_debt.request_info}")
print(f"Creation response time: {created_debt.response_raw.elapsed}")

# Debt lifecycle with monitoring
client.debts.ready(created_debt.id)
print("Debt marked as ready")

# Pause with reason and monitor
paused_debt = client.debts.pause(created_debt.id, {"reason": "customer request"})
print(f"Pause operation took: {paused_debt.response_raw.elapsed.total_seconds()}s")
```

### Customer Management

```python
from ophelos_sdk.models import Customer, ContactDetail

# Search customers with performance tracking
search_results = client.customers.search("email:john@example.com")

print(f"Customer search: {search_results.request_info['url']}")
print(f"Response time: {search_results.response_raw.elapsed.total_seconds()}s")

# Create customer with comprehensive contact details
customer_model = Customer(
    id="temp_customer",
    first_name="Jane",
    last_name="Smith",
    kind="individual",
    preferred_locale="en-GB",
    contact_details=[
        ContactDetail(
            id="temp_email",
            type="email",
            value="jane.smith@example.com",
            primary=True,
            usage="billing"
        ),
        ContactDetail(
            id="temp_phone",
            type="phone",
            value="+44987654321",
            usage="notifications"
        )
    ],
    metadata={
        "source": "api_integration",
        "priority": "high",
        "contact_preference": "email"
    }
)

# Show API body
print(f"Customer API body: {customer_model.to_api_body()}")

created_customer = client.customers.create(customer_model)

print(f"Customer created: {created_customer.id}")
print(f"Request details: {created_customer.request_info}")
print(f"Response time: {created_customer.response_raw.elapsed}")

# Update customer with request tracking
update_data = {
    "preferred_locale": "en-US",
    "metadata": {"updated_reason": "locale_change", "updated_at_custom": datetime.now().isoformat()}
}

updated_customer = client.customers.update(created_customer.id, update_data)

print(f"Update request body: {updated_customer.request_info['body']}")
print(f"Update response: {updated_customer.response_info['status_code']}")
```

### Contact Details Management

```python
from ophelos_sdk.models import ContactDetail

# Create contact details for a customer
contact_detail_model = ContactDetail(
    id="temp_contact",
    type="email",
    value="john.doe@example.com",
    primary=True,
    usage="billing",
    metadata={"verified": True, "source": "user_input"}
)

# Create contact detail
created_contact = client.contact_details.create(
    "cust_123",
    contact_detail_model,
    expand=["customer"]
)

print(f"Contact detail created: {created_contact.id}")
print(f"Request details: {created_contact.request_info}")
print(f"Response time: {created_contact.response_raw.elapsed}")

# Get specific contact detail
contact_detail = client.contact_details.get("cust_123", "cd_456")

print(f"Get contact detail request: {contact_detail.request_info}")
print(f"Contact type: {contact_detail.type}, Value: {contact_detail.value}")

# Update contact detail
update_data = {
    "usage": "notifications",
    "metadata": {"updated_reason": "preference_change"}
}

updated_contact = client.contact_details.update("cust_123", "cd_456", update_data)

print(f"Update request: {updated_contact.request_info}")
print(f"Updated usage: {updated_contact.usage}")

# List all contact details for customer
contact_details = client.contact_details.list("cust_123", limit=10)

print(f"Found {len(contact_details.data)} contact details")
print(f"List request time: {contact_details.response_raw.elapsed}")

# Soft delete contact detail
delete_response = client.contact_details.delete("cust_123", "cd_456")

print(f"Delete response: {delete_response}")
```

### Payment Operations

```python
from ophelos_sdk.models import Payment
from datetime import datetime

# List payments with monitoring
payments = client.payments.list(limit=20)

print(f"Payments list request: {payments.request_info}")
print(f"Response time: {payments.response_raw.elapsed.total_seconds()}s")

# Create payment with model
payment_model = Payment(
    id="temp_payment",
    amount=5000,  # Amount in cents
    transaction_ref="TXN-123456",
    transaction_at=datetime.now(),
    currency="GBP",
    metadata={
        "source": "bank_transfer",
        "verified": True,
        "reference": "BANK-REF-789"
    }
)

# Preview payment API body
print(f"Payment API body: {payment_model.to_api_body()}")

# Create payment for debt
created_payment = client.debts.create_payment("debt_123", payment_model)

print(f"Payment created: {created_payment.id}")
print(f"Creation request: {created_payment.request_info}")
print(f"Response details: {created_payment.response_info}")

# Get payment with request tracking
payment = client.payments.get(created_payment.id)

print(f"Get payment request: {payment.request_info}")
print(f"Response time: {payment.response_raw.elapsed}")
```

## Advanced Usage Patterns

### Concurrent Operations with Request Monitoring

```python
from concurrent.futures import ThreadPoolExecutor
import time

def process_debt_with_monitoring(debt_id):
    """Process debt with comprehensive request/response monitoring."""
    start_time = time.time()

    # Get debt details
    debt = client.debts.get(debt_id, expand=["customer", "payments"])

    end_time = time.time()

    result = {
        "debt_id": debt_id,
        "total_time": end_time - start_time,
        "api_response_time": debt.response_raw.elapsed.total_seconds(),
        "status_code": debt.response_info["status_code"],
        "request_url": debt.request_info["url"],
        "customer_name": debt.customer.full_name if debt.customer else None,
        "payment_count": len(debt.payments) if debt.payments else 0
    }

    return result

# Process multiple debts concurrently
debt_ids = ["debt_001", "debt_002", "debt_003", "debt_004", "debt_005"]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_debt_with_monitoring, debt_id) for debt_id in debt_ids]
    results = [future.result() for future in futures]

# Analyze performance
for result in results:
    print(f"Debt {result['debt_id']}:")
    print(f"  Total time: {result['total_time']:.3f}s")
    print(f"  API time: {result['api_response_time']:.3f}s")
    print(f"  Status: {result['status_code']}")
    print(f"  Customer: {result['customer_name']}")
    print()

# Calculate performance statistics
api_times = [r["api_response_time"] for r in results]
avg_api_time = sum(api_times) / len(api_times)
print(f"Average API response time: {avg_api_time:.3f}s")
```

### Pagination with Request Monitoring

```python
def paginate_with_monitoring(client, resource_name, **kwargs):
    """Paginate through all pages with request/response monitoring."""
    all_items = []
    page_count = 0
    total_api_time = 0

    # Get resource method (e.g., client.debts.list)
    resource = getattr(client, resource_name)
    list_method = getattr(resource, "list")

    cursor = None

    while True:
        page_count += 1

        # Set up parameters
        params = {**kwargs, "limit": kwargs.get("limit", 50)}
        if cursor:
            params["after"] = cursor

        # Get page
        page = list_method(**params)

        # Track timing
        api_time = page.response_raw.elapsed.total_seconds()
        total_api_time += api_time

        print(f"Page {page_count}: {len(page.data)} items, {api_time:.3f}s")

        # Add items
        all_items.extend(page.data)

        # Check for more pages
        if not page.has_more:
            break

        cursor = page.pagination['next']['after'] if page.pagination and 'next' in page.pagination else None

    print(f"Total: {len(all_items)} items across {page_count} pages")
    print(f"Total API time: {total_api_time:.3f}s")
    print(f"Average page time: {total_api_time/page_count:.3f}s")

    return all_items

# Usage
all_debts = paginate_with_monitoring(client, "debts", expand=["customer"])
```

### Comprehensive Error Handling with Request Context

```python
from ophelos_sdk.exceptions import (
    OphelosAPIError, AuthenticationError, TimeoutError,
    ParseError, UnexpectedError
)

def safe_api_call_with_context(operation_func, operation_name):
    """Execute API call with comprehensive error handling and context."""
    try:
        result = operation_func()
        print(f"✅ {operation_name} successful")
        print(f"   Request: {result.request_info['method']} {result.request_info['url']}")
        print(f"   Response: {result.response_info['status_code']} in {result.response_raw.elapsed.total_seconds():.3f}s")
        return result

    except OphelosAPIError as e:
        print(f"❌ {operation_name} API error: {e.message} (Status: {e.status_code})")
        print(f"   Request: {e.request_info}")
        print(f"   Response time: {e.response_raw.elapsed.total_seconds():.3f}s")
        raise

    except TimeoutError as e:
        print(f"⏱️ {operation_name} timed out: {e.message}")
        print(f"   Request details: {e.request_info}")  # Available even for timeouts
        raise

    except (ParseError, UnexpectedError) as e:
        print(f"💥 {operation_name} error: {e.message}")
        print(f"   Request context: {e.request_info}")
        if hasattr(e, 'original_error'):
            print(f"   Original error: {e.original_error}")
        raise

# Usage examples
debt = safe_api_call_with_context(
    lambda: client.debts.get("debt_123", expand=["customer"]),
    "Get debt with customer expansion"
)

customer = safe_api_call_with_context(
    lambda: client.customers.create({
        "first_name": "John",
        "last_name": "Doe",
        "contact_details": [{"type": "email", "value": "john@example.com"}]
    }),
    "Create new customer"
)
```

## Testing and Debugging

### Request/Response Debugging

```python
def debug_api_call(model_instance, operation_name):
    """Debug API call with full request/response details."""
    print(f"\n=== DEBUG: {operation_name} ===")

    # Request details
    print("Request:")
    print(f"  Method: {model_instance.request_info['method']}")
    print(f"  URL: {model_instance.request_info['url']}")
    print(f"  Headers: {model_instance.request_info['headers']}")

    if model_instance.request_info['body']:
        print(f"  Body: {model_instance.request_info['body']}")

    # Response details
    print("Response:")
    print(f"  Status: {model_instance.response_info['status_code']}")
    print(f"  Time: {model_instance.response_raw.elapsed.total_seconds():.3f}s")
    print(f"  Headers: {model_instance.response_info['headers']}")
    print(f"  Size: {len(model_instance.response_raw.content)} bytes")

# Usage
debt = client.debts.get("debt_123")
debug_api_call(debt, "Get Debt")

customer = client.customers.create({"first_name": "Test", "last_name": "User"})
debug_api_call(customer, "Create Customer")
```

### Model API Body Testing

```python
def test_model_api_body(model_instance, expected_fields=None, excluded_fields=None):
    """Test model API body generation."""
    api_body = model_instance.to_api_body()

    print(f"Model: {model_instance.__class__.__name__}")
    print(f"API Body: {api_body}")

    # Check expected fields
    if expected_fields:
        for field in expected_fields:
            assert field in api_body, f"Expected field '{field}' missing from API body"
        print(f"✅ Expected fields present: {expected_fields}")

    # Check excluded fields
    default_excluded = ["id", "object", "created_at", "updated_at"]
    all_excluded = default_excluded + (excluded_fields or [])

    for field in all_excluded:
        assert field not in api_body, f"Field '{field}' should be excluded from API body"
    print(f"✅ Excluded fields absent: {all_excluded}")

    return api_body

# Test customer model
customer = Customer(
    id="temp_123",
    first_name="John",
    last_name="Doe",
    contact_details=[ContactDetail(type="email", value="john@example.com")]
)

test_model_api_body(
    customer,
    expected_fields=["first_name", "last_name", "contact_details"],
    excluded_fields=["id", "object"]
)
```

## Development and Testing

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=ophelos_sdk tests/

# Run specific test categories
pytest tests/models/              # 143 model tests
pytest tests/test_resources.py    # Resource tests with error handling
pytest tests/test_auth.py          # Authentication tests

# Run tests with verbose output
pytest -v tests/

# Run only unit tests (exclude integration)
pytest -m "not integration"
```

### Code Quality

```bash
# Format code
black ophelos_sdk/ tests/ --line-length 120

# Check imports
isort ophelos_sdk/ tests/

# Lint code
flake8 ophelos_sdk/ tests/

# Type checking
mypy ophelos_sdk/

# Remove unused imports
autoflake --in-place --remove-all-unused-imports --recursive ophelos_sdk/
```

This comprehensive guide demonstrates the full capabilities of the Ophelos SDK, with special emphasis on the request/response transparency features that provide complete visibility into API interactions.
