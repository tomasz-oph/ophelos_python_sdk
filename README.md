# Ophelos Python SDK

Python SDK for the Ophelos API - a comprehensive debt management and customer communication platform.

## Installation

### From PyPI (when published)

```bash
pip install ophelos-sdk
```

### From Local Distribution

```bash
# Install from wheel (recommended)
pip install dist/ophelos_sdk-1.0.2-py3-none-any.whl

# Or install from source distribution  
pip install dist/ophelos-sdk-1.0.2.tar.gz

# Or install in development mode
pip install -e .
```

## Quick Start

```python
from ophelos_sdk import OphelosClient
from ophelos_sdk.models import Customer, Debt

# Initialize client with your credentials
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="staging"  # or "production"
)

# Option 1: Create using dictionaries (traditional approach)
customer = client.customers.create({
    "first_name": "John",
    "last_name": "Doe",
    "contact_details": [
        {"type": "email", "value": "john.doe@example.com", "primary": True}
    ]
})

# Option 2: Create using model instances (new approach)
from ophelos_sdk.models import Customer, ContactDetail

customer_model = Customer(
    id="temp_cust_123",  # Temporary ID
    first_name="Jane",
    last_name="Smith",
    contact_details=[
        ContactDetail(
            id="temp_cd_123",
            type="email",
            value="jane.smith@example.com",
            primary=True
        )
    ]
)

# Pass model directly to API - automatic conversion to API body
customer = client.customers.create(customer_model)

# Create a debt using model instance
debt_model = Debt(
    id="temp_debt_123",
    customer=customer.id,  # Use real customer ID
    organisation="org_123",
    currency="GBP",
    reference_code="DEBT-001",
    kind="purchased"
)

debt = client.debts.create(debt_model)

# Prepare the debt for processing
client.debts.ready(debt.id)
```

📋 **For comprehensive usage examples and advanced features, see [USAGE.md](USAGE.md)**

## Features

- **Complete API Coverage**: All Ophelos API endpoints supported
- **Type Safety**: Full type hints and Pydantic models with automatic API body generation
- **Model-First Approach**: Create and pass Pydantic model instances directly to API calls
- **Smart Field Management**: Automatic exclusion of server-generated fields and intelligent relationship handling
- **Authentication**: Automatic OAuth2 token management with thread-safe token caching
- **Multi-Tenant Support**: Automatic tenant header injection for multi-tenant applications
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Pagination**: Built-in pagination support
- **Search**: Advanced search functionality
- **Webhooks**: Webhook event handling and validation
- **Concurrent Safe**: Thread-safe for use with concurrent request patterns

## Model-First API Usage

The Ophelos SDK supports both traditional dictionary-based API calls and a modern model-first approach using Pydantic models.

### Direct Model Usage

```python
from ophelos_sdk.models import Customer, Debt, Payment, ContactDetail

# Create models with type safety and validation
customer = Customer(
    id="temp_123",  # Temporary ID for creation
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

# Pass model directly to API - automatic conversion
created_customer = client.customers.create(customer)
```

### Smart API Body Generation

Models automatically generate appropriate API request bodies:

```python
# Get the API body that would be sent
api_body = customer.to_api_body()

# Automatically excludes server-generated fields:
# - id, object, created_at, updated_at are removed
# - Only fields appropriate for create/update operations are included
# - Nested models are handled intelligently

print(api_body)
# Output: {
#   "first_name": "John",
#   "last_name": "Doe", 
#   "contact_details": [
#     {"type": "email", "value": "john@example.com", "primary": True}
#   ]
# }
```

### Intelligent Relationship Handling

The SDK handles relationships intelligently:

```python
# For debt creation, customer/organisation references become ID references
debt = Debt(
    id="temp_debt",
    customer=existing_customer,  # Model instance with real ID
    organisation="org_123",      # String ID
    currency="GBP"
)

api_body = debt.to_api_body()
# customer field becomes: "customer": "cust_real_id_123"
# Other nested models remain as full objects

# Create the debt
created_debt = client.debts.create(debt)
```

## API Resources

### Debt Management
- Create, update, and manage debts using dictionaries or model instances
- Debt lifecycle operations (ready, pause, resume, withdraw)
- Payment processing and tracking with automatic field management

### Customer Management
- Customer CRUD operations with full model support
- Search and filtering
- Contact detail management with nested model handling

### Payment Management
- Payment creation and tracking with smart field exclusion
- Payment plan management
- External payment recording with automatic API body generation

### Organisation Management
- Organisation setup and configuration
- Contact detail management

### Invoice Management
- Invoice creation and management with model support
- Line item handling with automatic field filtering

### Communication Management
- Communication tracking
- Outbound communication management

## Authentication

The Ophelos API uses OAuth2 Client Credentials flow. You'll need:

1. **Client ID**: Your application's client identifier
2. **Client Secret**: Your application's client secret
3. **Audience**: Your API identifier

Contact Ophelos support to obtain these credentials.

```python
# Environment configuration
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    audience="your_audience",
    environment="production"  # "development", "staging", or "production"
)

# For local development (uses http://api.localhost:3000)
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience", 
    environment="development"
)
```

### Multi-Tenant Support

For multi-tenant applications, you can specify a `tenant_id` to automatically include the `OPHELOS_TENANT_ID` header in all API requests:

```python
# Initialize client with tenant ID
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production",
    tenant_id="tenant_123"  # Automatically adds OPHELOS_TENANT_ID header
)

# All requests will include the tenant header
customer = client.customers.create({
    "first_name": "John",
    "last_name": "Doe"
})
# ^ This request includes: OPHELOS_TENANT_ID: tenant_123

# You can also create different clients for different tenants
tenant_a_client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    tenant_id="tenant_a"
)

tenant_b_client = OphelosClient(
    client_id="your_client_id", 
    client_secret="your_client_secret",
    audience="your_audience",
    tenant_id="tenant_b"
)
```

## Examples

### Working with Debts

```python
from ophelos_sdk.models import Debt

# List debts with pagination
debts = client.debts.list(limit=10)

# Search debts
results = client.debts.search("status:paying AND updated_at>=2024-01-01")

# Get debt details with expansions
debt = client.debts.get("debt_123", expand=["customer", "payments"])

# Option 1: Update using dictionary
updated_debt = client.debts.update("debt_123", {
    "metadata": {"case_id": "12345"}
})

# Option 2: Update using model instance
debt_model = Debt(
    id="temp_debt_update",
    metadata={"case_id": "12345", "priority": "high"},
    tags=["urgent", "follow-up"]
)
updated_debt = client.debts.update("debt_123", debt_model)

# Generate API body from model (useful for debugging)
api_body = debt_model.to_api_body()
print(f"API body: {api_body}")
# Output: {'metadata': {'case_id': '12345', 'priority': 'high'}, 'tags': ['urgent', 'follow-up']}
```

### Working with Customers

```python
from ophelos_sdk.models import Customer, ContactDetail

# Search customers by email
customers = client.customers.search("email:john@example.com")

# Option 1: Update using dictionary
customer = client.customers.update("cust_123", {
    "preferred_locale": "en-GB",
    "metadata": {"updated_reason": "customer request"}
})

# Option 2: Update using model instance with nested objects
customer_model = Customer(
    id="temp_update",
    preferred_locale="en-GB",
    contact_details=[
        ContactDetail(
            id="temp_cd_1",
            type="email",
            value="new.email@example.com",
            primary=True
        ),
        ContactDetail(
            id="temp_cd_2", 
            type="phone",
            value="+44123456789",
            usage="billing"
        )
    ],
    metadata={"updated_reason": "customer request", "source": "api"}
)

customer = client.customers.update("cust_123", customer_model)

# Preview what will be sent to API
api_body = customer_model.to_api_body()
# Automatically excludes server fields (id, object, created_at, updated_at)
# Includes nested contact_details as full objects (not ID references)
```

### Working with Payments

```python
from ophelos_sdk.models import Payment
from datetime import datetime

# Option 1: Create external payment using dictionary
payment = client.debts.create_payment("debt_123", {
    "amount": 5000,
    "transaction_at": "2024-01-15T10:00:00Z",
    "transaction_ref": "TXN-12345"
})

# Option 2: Create payment using model instance
payment_model = Payment(
    id="temp_payment",
    debt="debt_123",  # Will be excluded from API body (set by endpoint context)
    amount=5000,
    transaction_at=datetime.now(),
    transaction_ref="TXN-12345",
    currency="GBP",
    metadata={"source": "bank_transfer", "reference": "REF-001"}
)

payment = client.debts.create_payment("debt_123", payment_model)

# See what gets sent to API
api_body = payment_model.to_api_body()
# Note: 'debt' field is automatically excluded as it's set by the endpoint context
# Only includes: amount, transaction_at, transaction_ref, currency, metadata

# List payments for a debt
payments = client.debts.list_payments("debt_123")
```

### Error Handling

```python
from ophelos_sdk.exceptions import OphelosAPIError, AuthenticationError

try:
    debt = client.debts.get("invalid_debt_id")
except OphelosAPIError as e:
    print(f"API Error: {e.message} (Status: {e.status_code})")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

### Webhook Handling

```python
from ophelos_sdk.webhooks import WebhookHandler

# Initialize webhook handler
webhook_handler = WebhookHandler("your_webhook_secret")

# Validate and parse webhook
try:
    event = webhook_handler.verify_and_parse(
        payload=request.body,
        signature=request.headers.get("Ophelos-Signature")
    )
    
    if event.type == "debt.created":
        print(f"New debt created: {event.data.id}")
        
except Exception as e:
    print(f"Webhook validation failed: {e}")
```

### Concurrent Usage with Multi-Tenant Support

```python
from concurrent.futures import ThreadPoolExecutor
from ophelos_sdk import OphelosClient

# Create tenant-specific clients
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

def process_tenant_debts(tenant_id):
    """Process debts for a specific tenant concurrently."""
    client = clients[tenant_id]
    # All requests automatically include OPHELOS_TENANT_ID header
    debts = client.debts.list(limit=50)
    return f"Processed {len(debts.data)} debts for {tenant_id}"

# Process multiple tenants concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(process_tenant_debts, "tenant_a"),
        executor.submit(process_tenant_debts, "tenant_b")
    ]
    
    for future in futures:
        result = future.result()
        print(result)
```

## API Reference

### Client Configuration

```python
OphelosClient(
    client_id: str,
    client_secret: str, 
    audience: str,
    environment: str = "staging",  # "development", "staging", or "production"
    tenant_id: Optional[str] = None,  # For multi-tenant applications
    timeout: int = 30,
    max_retries: int = 3
)
```

**Parameters:**
- `client_id`: OAuth2 client identifier
- `client_secret`: OAuth2 client secret
- `audience`: API audience/identifier
- `environment`: Target environment (`"development"`, `"staging"`, or `"production"`)
- `tenant_id`: Optional tenant identifier for multi-tenant applications (adds `OPHELOS_TENANT_ID` header)
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum number of retries for failed requests

### Resource Managers

- `client.debts` - Debt management operations
- `client.customers` - Customer management operations  
- `client.organisations` - Organisation management operations
- `client.payments` - Payment management operations
- `client.invoices` - Invoice management operations
- `client.webhooks` - Webhook management operations

## Development

```bash
# Clone the repository
git clone https://github.com/ophelos/ophelos-python-sdk.git
cd ophelos-python-sdk

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 ophelos_sdk/
mypy ophelos_sdk/
```

## Support

- **API Reference**: [https://api.ophelos.com](https://api.ophelos.com)
- **Support Email**: support@ophelos.com
- **Issues**: [GitHub Issues](https://github.com/tomasz-oph/ophelos_python_sdk/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 