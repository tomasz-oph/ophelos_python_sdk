# Ophelos SDK Usage Guide

This guide shows how to install and use the Ophelos SDK from the local distribution files.

## Installation

### Option 1: Install from Wheel (Recommended)

Install directly from the built wheel file:

```bash
pip install dist/ophelos_sdk-1.0.2-py3-none-any.whl
```

### Option 2: Install from Source Distribution

Install from the source distribution:

```bash
pip install dist/ophelos-sdk-1.0.2.tar.gz
```

### Option 3: Development Installation

For development with live changes:

```bash
pip install -e .
```

## Basic Usage

### 1. Initialize the Client

```python
from ophelos_sdk import OphelosClient

# Option 1: OAuth2 Authentication (Recommended)
# For staging environment (default)
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="staging"
)

# For production environment
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production"
)

# For local development
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="development"  # Uses http://api.localhost:3000
)

# Option 2: Direct Access Token Authentication
# If you already have a valid access token
client = OphelosClient(
    access_token="your_access_token",
    environment="production"
)

# Option 3: Multi-tenant applications
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production",
    tenant_id="tenant_123"  # Automatically adds OPHELOS_TENANT_ID header to all requests
)

# Multi-tenant with access token
client = OphelosClient(
    access_token="your_access_token",
    environment="production",
    tenant_id="tenant_123"
)
```

### 2. Multi-Tenant Usage Patterns

For applications serving multiple tenants, you can use different approaches:

#### Option A: Multiple Client Instances

```python
# Create separate clients for each tenant
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

# Use tenant-specific client
def get_tenant_debts(tenant_id):
    client = clients[tenant_id]
    return client.debts.list(limit=50)

# All requests automatically include the correct OPHELOS_TENANT_ID header
debts_a = get_tenant_debts("tenant_a")
debts_b = get_tenant_debts("tenant_b")
```

#### Option B: Dynamic Client Creation

```python
def create_tenant_client(tenant_id):
    return OphelosClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        audience="your_audience",
        environment="production",
        tenant_id=tenant_id
    )

# Create client on-demand
def process_tenant_data(tenant_id, debt_ids):
    client = create_tenant_client(tenant_id)
    
    results = []
    for debt_id in debt_ids:
        debt = client.debts.get(debt_id)  # Includes OPHELOS_TENANT_ID: {tenant_id}
        results.append(debt)
    
    return results
```

#### Option C: Concurrent Multi-Tenant Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_tenant_concurrently(tenant_configs):
    """Process multiple tenants concurrently with thread-safe authentication."""
    
    def process_single_tenant(tenant_config):
        client = OphelosClient(
            client_id="your_client_id", 
            client_secret="your_client_secret",
            audience="your_audience",
            tenant_id=tenant_config["tenant_id"]
        )
        
        # Process tenant data
        debts = client.debts.list(limit=100)
        return {
            "tenant_id": tenant_config["tenant_id"],
            "debt_count": len(debts.data),
            "status": "success"
        }
    
    # Process tenants concurrently - authentication is thread-safe
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_single_tenant, config) 
            for config in tenant_configs
        ]
        
        results = [future.result() for future in futures]
    
    return results

# Usage
tenant_configs = [
    {"tenant_id": "tenant_a"},
    {"tenant_id": "tenant_b"},
    {"tenant_id": "tenant_c"}
]

results = process_tenant_concurrently(tenant_configs)
for result in results:
    print(f"Tenant {result['tenant_id']}: {result['debt_count']} debts")
```

### 3. Working with Debts

```python
from ophelos_sdk.models import Debt

# List debts
debts = client.debts.list(limit=10)
print(f"Found {len(debts.data)} debts")

# Get a specific debt
debt = client.debts.get("debt_123456789", expand=["customer", "payments"])
print(f"Debt amount: {debt.summary.amount_total} {debt.currency}")

# Search debts
results = client.debts.search("status:paying", limit=20)
for debt in results.data:
    print(f"Debt {debt.id}: {debt.status}")

# Option 1: Create a new debt using dictionary
new_debt = client.debts.create({
    "customer": "cust_123456789",
    "organisation": "org_123456789",
    "currency": "GBP",
    "reference_code": "REF-001",
    "kind": "purchased",
    "metadata": {"case_id": "12345"}
})

# Option 2: Create using model instance (recommended)
debt_model = Debt(
    id="temp_debt_123",  # Temporary ID for creation
    customer="cust_123456789",  # Customer ID reference
    organisation="org_123456789",  # Organisation ID reference
    currency="GBP",
    reference_code="REF-001",
    kind="purchased",
    tags=["urgent", "high-priority"],
    metadata={"case_id": "12345", "source": "api"}
)

# Pass model directly - automatic API body generation
new_debt = client.debts.create(debt_model)

# Preview API body before sending (useful for debugging)
api_body = debt_model.to_api_body()
print(f"API body: {api_body}")
# Server fields (id, object, created_at, updated_at) automatically excluded

# Option 1: Update debt metadata using dictionary
updated_debt = client.debts.update("debt_123456789", {
    "metadata": {"case_id": "12345", "priority": "high"}
})

# Option 2: Update using model instance
update_model = Debt(
    id="temp_update",
    metadata={"case_id": "12345", "priority": "high", "updated_by": "api"},
    tags=["high-priority", "reviewed"]
)
updated_debt = client.debts.update("debt_123456789", update_model)

# Debt lifecycle operations
client.debts.ready("debt_123456789")  # Mark as ready
client.debts.pause("debt_123456789", {"reason": "customer request"})
client.debts.resume("debt_123456789")
```

### 4. Working with Customers

```python
from ophelos_sdk.models import Customer, ContactDetail

# List customers
customers = client.customers.list(limit=10)

# Get a specific customer
customer = client.customers.get("cust_123456789")
print(f"Customer: {customer.full_name}")

# Search customers
results = client.customers.search("email:john@example.com")

# Option 1: Create a new customer using dictionary
new_customer = client.customers.create({
    "first_name": "John",
    "last_name": "Doe",
    "kind": "individual",
    "preferred_locale": "en",
    "contact_details": [
        {"type": "email", "value": "john@example.com", "primary": True},
        {"type": "phone", "value": "+44123456789", "usage": "billing"}
    ],
    "metadata": {"organisation_id": "org_123456789"}
})

# Option 2: Create using model instance with nested objects
customer_model = Customer(
    id="temp_cust_123",
    first_name="Jane",
    last_name="Smith",
    kind="individual",
    preferred_locale="en-GB",
    contact_details=[
        ContactDetail(
            id="temp_cd_1",
            type="email",
            value="jane.smith@example.com",
            primary=True,
            usage="billing"
        ),
        ContactDetail(
            id="temp_cd_2",
            type="phone", 
            value="+44987654321",
            usage="notifications"
        )
    ],
    metadata={"organisation_id": "org_123456789", "source": "api"}
)

# Create customer - nested contact details handled automatically
new_customer = client.customers.create(customer_model)

# See what gets sent to API
api_body = customer_model.to_api_body()
print(f"API body: {api_body}")
# contact_details included as full objects (not ID references)
# Server fields automatically excluded from nested objects

# Option 1: Update customer information using dictionary
updated_customer = client.customers.update("cust_123456789", {
    "preferred_locale": "en-GB",
    "metadata": {"updated_by": "system"}
})

# Option 2: Update using model instance
update_model = Customer(
    id="temp_update",
    preferred_locale="en-GB",
    metadata={"updated_by": "system", "last_contact": "2024-01-15"}
)
updated_customer = client.customers.update("cust_123456789", update_model)
```

### 5. Working with Payments

```python
from ophelos_sdk.models import Payment
from datetime import datetime

# List all payments
payments = client.payments.list(limit=20)

# Get a specific payment
payment = client.payments.get("pay_123456789")
print(f"Payment: {payment.amount} {payment.currency} - {payment.status}")

# Search payments
successful_payments = client.payments.search("status:succeeded")

# Option 1: Create a payment for a debt using dictionary
new_payment = client.debts.create_payment("debt_123456789", {
    "amount": 5000,  # Amount in cents
    "transaction_ref": "TXN-123",
    "transaction_at": "2024-01-15T10:00:00Z",
    "currency": "GBP"
})

# Option 2: Create payment using model instance
payment_model = Payment(
    id="temp_payment_123",
    debt="debt_123456789",  # Will be excluded from API body (set by endpoint)
    amount=5000,
    transaction_ref="TXN-456",
    transaction_at=datetime.now(),
    currency="GBP",
    metadata={
        "source": "bank_transfer",
        "reference": "BANK-REF-789",
        "verified": True
    }
)

# Create payment - 'debt' field automatically excluded from API body
new_payment = client.debts.create_payment("debt_123456789", payment_model)

# Preview what gets sent to API
api_body = payment_model.to_api_body()
print(f"Payment API body: {api_body}")
# Output excludes: debt (set by endpoint), id, object, created_at, updated_at
# Includes: amount, transaction_ref, transaction_at, currency, metadata

# List payments for a specific debt
debt_payments = client.debts.list_payments("debt_123456789")
```

### 6. Working with Organisations

```python
# List organisations
organisations = client.organisations.list()

# Get a specific organisation
org = client.organisations.get("org_123456789")
print(f"Organisation: {org.name}")

# Update organisation
updated_org = client.organisations.update("org_123456789", {
    "description": "Updated description",
    "metadata": {"industry": "finance"}
})
```

### 7. Webhook Handling

```python
from ophelos_sdk import WebhookHandler, construct_event

# Initialize webhook handler
webhook_handler = WebhookHandler("your_webhook_secret")

# In your webhook endpoint
def handle_webhook(request):
    payload = request.body.decode('utf-8')
    signature = request.headers.get('Ophelos-Signature')
    
    try:
        # Verify and parse the webhook event
        event = webhook_handler.verify_and_parse(payload, signature)
        
        # Handle different event types
        if event.type == "debt.created":
            print(f"New debt created: {event.data['id']}")
        elif event.type == "payment.succeeded":
            print(f"Payment succeeded: {event.data['id']}")
        
        return {"status": "success"}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error"}, 400

# Alternative convenience function
def handle_webhook_simple(request):
    event = construct_event(
        payload=request.body.decode('utf-8'),
        signature_header=request.headers.get('Ophelos-Signature'),
        webhook_secret="your_webhook_secret"
    )
    
    # Process the event
    print(f"Received {event.type} event")
```

## Error Handling

The SDK provides comprehensive error handling with graceful fallback for invalid API responses:

```python
from ophelos_sdk import (
    OphelosError, OphelosAPIError, AuthenticationError,
    ValidationError, NotFoundError, RateLimitError
)

try:
    debt = client.debts.get("nonexistent_debt")
except NotFoundError:
    print("Debt not found")
except AuthenticationError:
    print("Authentication failed - check your credentials")
except ValidationError as e:
    print(f"Validation error: {e}")
    if hasattr(e, 'response_data'):
        print(f"Response data: {e.response_data}")
except RateLimitError:
    print("Rate limit exceeded - please retry later")
except OphelosAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
    if hasattr(e, 'response_data'):
        print(f"Full response: {e.response_data}")
except OphelosError as e:
    print(f"General Ophelos error: {e}")

# The SDK automatically handles invalid API responses
# by falling back to raw dictionary data when model parsing fails
try:
    # If the API returns malformed data, you'll get a dict instead of a model
    result = client.debts.get("debt_with_invalid_data")
    if isinstance(result, dict):
        print("Received raw data due to parsing error:", result)
    else:
        print("Received valid debt model:", result.id)
except Exception as e:
    print(f"Request failed: {e}")
```

## Configuration Options

### Environment Variables

You can also configure the client using environment variables:

```bash
# OAuth2 Authentication
export OPHELOS_CLIENT_ID="your_client_id"
export OPHELOS_CLIENT_SECRET="your_client_secret"
export OPHELOS_AUDIENCE="your_audience"

# OR Direct Access Token Authentication
export OPHELOS_ACCESS_TOKEN="your_access_token"

# Common Configuration
export OPHELOS_ENVIRONMENT="staging"
export OPHELOS_TENANT_ID="tenant_123"  # Optional for multi-tenant applications
```

```python
import os
from ophelos_sdk import OphelosClient

# OAuth2 authentication from environment
client = OphelosClient(
    client_id=os.getenv("OPHELOS_CLIENT_ID"),
    client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
    audience=os.getenv("OPHELOS_AUDIENCE"),
    environment=os.getenv("OPHELOS_ENVIRONMENT", "staging"),
    tenant_id=os.getenv("OPHELOS_TENANT_ID")  # Will be None if not set
)

# OR Access token authentication from environment
client = OphelosClient(
    access_token=os.getenv("OPHELOS_ACCESS_TOKEN"),
    environment=os.getenv("OPHELOS_ENVIRONMENT", "staging"),
    tenant_id=os.getenv("OPHELOS_TENANT_ID")
)
```

### Timeout and Retry Configuration

```python
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="staging",
    tenant_id="optional_tenant_id",  # For multi-tenant applications
    timeout=60,  # Request timeout in seconds
    max_retries=5  # Maximum retry attempts
)
```

### Complete Configuration Reference

```python
# OAuth2 Authentication
client = OphelosClient(
    client_id="your_client_id",           # Required: OAuth2 client ID
    client_secret="your_client_secret",   # Required: OAuth2 client secret
    audience="your_audience",             # Required: API audience/identifier
    environment="production",             # Optional: "development", "staging", or "production"
    tenant_id="tenant_123",              # Optional: For multi-tenant applications
    timeout=30,                          # Optional: Request timeout in seconds (default: 30)
    max_retries=3                        # Optional: Max retry attempts (default: 3)
)

# OR Direct Access Token Authentication
client = OphelosClient(
    access_token="your_access_token",     # Required: Pre-obtained access token
    environment="production",             # Optional: "development", "staging", or "production"
    tenant_id="tenant_123",              # Optional: For multi-tenant applications
    timeout=30,                          # Optional: Request timeout in seconds (default: 30)
    max_retries=3                        # Optional: Max retry attempts (default: 3)
)
```

## Pagination

Handle paginated responses:

```python
# Get first page
debts = client.debts.list(limit=10)

# Check if there are more results
if debts.has_more:
    print(f"Total count: {debts.total_count}")
    
    # Get next page using the last item ID
    last_debt_id = debts.data[-1].id
    next_page = client.debts.list(limit=10, after=last_debt_id)
```

## Model-First API Usage

The Ophelos SDK provides comprehensive Pydantic models that can be used directly with API calls, offering type safety, validation, and automatic API body generation.

### Understanding Model API Bodies

Each model knows which fields are appropriate for API create/update operations:

```python
from ophelos_sdk.models import Customer, Debt, Payment, ContactDetail

# Create a customer model
customer = Customer(
    id="temp_123",  # Temporary ID (will be excluded from API body)
    first_name="John",
    last_name="Doe",
    contact_details=[
        ContactDetail(
            id="temp_cd_1",
            type="email",
            value="john@example.com",
            primary=True
        )
    ]
)

# Generate API body - only includes fields appropriate for creation
api_body = customer.to_api_body()
print(api_body)
# Output: {
#   "first_name": "John",
#   "last_name": "Doe",
#   "contact_details": [
#     {"type": "email", "value": "john@example.com", "primary": True}
#   ]
# }

# Server-generated fields are automatically excluded:
# - id, object, created_at, updated_at
```

### Smart Relationship Handling

The SDK handles different types of relationships intelligently:

```python
from ophelos_sdk.models import Debt, Customer

# Scenario 1: Customer/Organisation references in debt creation
# These become ID references in the API body
debt_with_references = Debt(
    id="temp_debt",
    customer="cust_123",  # String ID - preserved as-is
    organisation=existing_customer,  # Model with real ID - becomes ID reference
    currency="GBP"
)

api_body = debt_with_references.to_api_body()
# customer field: "cust_123" (string preserved)
# organisation field: "org_real_id" (extracted from model.id)

# Scenario 2: Nested objects in customer creation
# These remain as full objects in the API body
customer_with_contacts = Customer(
    id="temp_cust",
    first_name="Jane",
    contact_details=[
        ContactDetail(
            id="temp_cd_1",
            type="email",
            value="jane@example.com"
        )
    ]
)

api_body = customer_with_contacts.to_api_body()
# contact_details field: [{"type": "email", "value": "jane@example.com"}]
# (full object with server fields excluded)
```

### Field Control and Validation

Models automatically determine which fields are appropriate for API requests:

```python
# Payment model example - debt field excluded from API body
payment = Payment(
    id="temp_pay",
    debt="debt_123",  # Set for context but excluded from API body
    amount=5000,
    transaction_ref="TXN-123",
    currency="GBP"
)

api_body = payment.to_api_body()
# Only includes: amount, transaction_ref, currency, transaction_at, metadata
# Excludes: debt (set by endpoint context), id, object, created_at, updated_at

# The SDK automatically excludes server-generated fields:
# - id, object, created_at, updated_at (always excluded)
# - Context-specific fields (like 'debt' in payment creation)

# Test field exclusion
assert "id" not in api_body
assert "debt" not in api_body
assert "amount" in api_body
print("✅ Field exclusion working correctly")
```

### Robust Error Handling and Data Validation

The SDK provides intelligent error handling with graceful fallbacks:

```python
# The SDK handles invalid API responses gracefully
# If the API returns malformed data, it falls back to raw dictionaries

# Example: API returns invalid debt data
try:
    # This might return either a Debt model or raw dict
    result = client.debts.get("some_debt_id")
    
    if isinstance(result, Debt):
        print(f"Valid debt model: {result.id}")
        print(f"Amount: {result.summary.amount_total}")
    elif isinstance(result, dict):
        print(f"Raw data (parsing failed): {result}")
        # Handle raw data appropriately
        debt_id = result.get("id", "unknown")
        print(f"Debt ID from raw data: {debt_id}")
    
except OphelosAPIError as e:
    print(f"API error: {e.message}")
    if hasattr(e, 'response_data'):
        print(f"Response data: {e.response_data}")
```

### Model Usage Patterns

#### Pattern 1: Direct Model Creation

```python
# Create and use models directly
customer = Customer(
    id="temp_123",
    first_name="John",
    last_name="Doe"
)

created_customer = client.customers.create(customer)
print(f"Created customer: {created_customer.id}")
```

#### Pattern 2: API Body Preview

```python
# Preview what will be sent before making the API call
debt = Debt(
    id="temp_debt",
    customer="cust_123",
    organisation="org_456",
    currency="GBP",
    metadata={"case_id": "12345"}
)

# See the API body
api_body = debt.to_api_body()
print(f"Will send: {api_body}")

# Then create
created_debt = client.debts.create(debt)
```

#### Pattern 3: Model Factory Functions

```python
def create_customer_model(first_name, last_name, email, phone=None):
    """Factory function to create customer models."""
    contact_details = [
        ContactDetail(
            id=f"temp_email_{first_name.lower()}",
            type="email",
            value=email,
            primary=True
        )
    ]
    
    if phone:
        contact_details.append(
            ContactDetail(
                id=f"temp_phone_{first_name.lower()}",
                type="phone",
                value=phone,
                usage="billing"
            )
        )
    
    return Customer(
        id=f"temp_cust_{first_name.lower()}_{last_name.lower()}",
        first_name=first_name,
        last_name=last_name,
        contact_details=contact_details
    )

# Use the factory
customer = create_customer_model("John", "Doe", "john@example.com", "+44123456789")
created_customer = client.customers.create(customer)
```

#### Pattern 4: Batch Operations with Models

```python
# Create multiple customers using models
customers_data = [
    {"first_name": "John", "last_name": "Doe", "email": "john@example.com"},
    {"first_name": "Jane", "last_name": "Smith", "email": "jane@example.com"},
    {"first_name": "Bob", "last_name": "Wilson", "email": "bob@example.com"}
]

created_customers = []
for data in customers_data:
    customer_model = Customer(
        id=f"temp_{data['first_name'].lower()}",
        first_name=data["first_name"],
        last_name=data["last_name"],
        contact_details=[
            ContactDetail(
                id=f"temp_email_{data['first_name'].lower()}",
                type="email",
                value=data["email"],
                primary=True
            )
        ]
    )
    
    created_customer = client.customers.create(customer_model)
    created_customers.append(created_customer)

print(f"Created {len(created_customers)} customers")
```

## Advanced Usage

### Thread-Safe Concurrent Operations

The SDK is fully thread-safe and optimized for concurrent usage:

```python
from concurrent.futures import ThreadPoolExecutor
import time

# Single client instance can be safely used across multiple threads
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    tenant_id="tenant_123"  # Optional for multi-tenant apps
)

def fetch_debt_data(debt_id):
    """Function to be called concurrently."""
    debt = client.debts.get(debt_id, expand=["customer", "payments"])
    return {
        "debt_id": debt_id,
        "amount": debt.summary.amount_total,
        "customer": debt.customer.full_name if debt.customer else None,
        "payment_count": len(debt.payments) if debt.payments else 0
    }

# Process multiple debts concurrently
debt_ids = ["debt_001", "debt_002", "debt_003", "debt_004", "debt_005"]

with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit all tasks
    futures = [executor.submit(fetch_debt_data, debt_id) for debt_id in debt_ids]
    
    # Collect results
    results = [future.result() for future in futures]

# Authentication token is automatically shared across all threads
for result in results:
    print(f"Debt {result['debt_id']}: {result['amount']} ({result['payment_count']} payments)")
```

### Expanding Related Resources

```python
# Get debt with expanded customer and payment information
debt = client.debts.get(
    "debt_123456789", 
    expand=["customer", "payments", "organisation"]
)

print(f"Customer: {debt.customer.full_name}")
print(f"Payments: {len(debt.payments)} payments")
```

### Batch Operations

```python
# Process multiple debts
debt_ids = ["debt_001", "debt_002", "debt_003"]

for debt_id in debt_ids:
    try:
        debt = client.debts.get(debt_id)
        if debt.status.value == "prepared":
            client.debts.ready(debt_id)
            print(f"Marked {debt_id} as ready")
    except Exception as e:
        print(f"Error processing {debt_id}: {e}")
```

## Testing Your Integration

Test your connection and explore the comprehensive test coverage:

```python
# Test basic connectivity
if client.test_connection():
    print("✅ Connected to Ophelos API successfully")
else:
    print("❌ Failed to connect to Ophelos API")

# Test with your actual data
try:
    tenant = client.tenants.get_me()
    print(f"✅ Authenticated as: {tenant.name}")
except Exception as e:
    print(f"❌ Authentication failed: {e}")

# Test model functionality
from ophelos_sdk.models import Customer, ContactDetail

# Create a test customer model
customer = Customer(
    id="temp_test",
    first_name="Test",
    last_name="User",
    contact_details=[
        ContactDetail(
            id="temp_email",
            type="email",
            value="test@example.com",
            primary=True
        )
    ]
)

# Test API body generation
api_body = customer.to_api_body()
print(f"✅ Model API body generation works: {api_body}")

# Verify server fields are excluded
assert "id" not in api_body
assert "object" not in api_body
assert "created_at" not in api_body
assert "updated_at" not in api_body
print("✅ Server field exclusion working correctly")
```

## SDK Test Coverage

The Ophelos SDK includes comprehensive test coverage:

- **155+ Model Tests**: Complete coverage of all Pydantic models including API body generation, field validation, enum handling, and relationship processing
- **Resource Tests**: Full coverage of all API resource managers with error handling and fallback mechanisms
- **Authentication Tests**: OAuth2 and access token authentication with thread-safety validation
- **Integration Tests**: End-to-end testing with real API endpoints (when credentials are provided)
- **Error Handling Tests**: Validation of graceful fallback for invalid API responses

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/models/          # 155+ model tests
pytest tests/test_resources.py  # Resource and error handling tests
pytest tests/test_auth.py       # Authentication tests
pytest tests/test_client.py     # Client configuration tests

# Run with coverage
pytest --cov=ophelos_sdk tests/
``` 