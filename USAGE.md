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

# For multi-tenant applications
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="production",
    tenant_id="tenant_123"  # Automatically adds OPHELOS_TENANT_ID header to all requests
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

# Create a new debt
new_debt = client.debts.create({
    "customer": "cust_123456789",
    "organisation": "org_123456789",
    "currency": "GBP",
    "reference_code": "REF-001",
    "kind": "purchased",
    "metadata": {"case_id": "12345"}
})

# Update debt metadata
updated_debt = client.debts.update("debt_123456789", {
    "metadata": {"case_id": "12345", "priority": "high"}
})

# Debt lifecycle operations
client.debts.ready("debt_123456789")  # Mark as ready
client.debts.pause("debt_123456789", {"reason": "customer request"})
client.debts.resume("debt_123456789")
```

### 4. Working with Customers

```python
# List customers
customers = client.customers.list(limit=10)

# Get a specific customer
customer = client.customers.get("cust_123456789")
print(f"Customer: {customer.full_name}")

# Search customers
results = client.customers.search("email:john@example.com")

# Create a new customer
new_customer = client.customers.create({
    "first_name": "John",
    "last_name": "Doe",
    "kind": "individual",
    "preferred_locale": "en",
    "metadata": {"organisation_id": "org_123456789"}
})

# Update customer information
updated_customer = client.customers.update("cust_123456789", {
    "preferred_locale": "en-GB",
    "metadata": {"updated_by": "system"}
})
```

### 5. Working with Payments

```python
# List all payments
payments = client.payments.list(limit=20)

# Get a specific payment
payment = client.payments.get("pay_123456789")
print(f"Payment: {payment.amount} {payment.currency} - {payment.status}")

# Search payments
successful_payments = client.payments.search("status:succeeded")

# Create a payment for a debt
new_payment = client.debts.create_payment("debt_123456789", {
    "amount": 5000,  # Amount in cents
    "transaction_ref": "TXN-123",
    "transaction_at": "2024-01-15T10:00:00Z"
})

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
except RateLimitError:
    print("Rate limit exceeded - please retry later")
except OphelosAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except OphelosError as e:
    print(f"General Ophelos error: {e}")
```

## Configuration Options

### Environment Variables

You can also configure the client using environment variables:

```bash
export OPHELOS_CLIENT_ID="your_client_id"
export OPHELOS_CLIENT_SECRET="your_client_secret"
export OPHELOS_AUDIENCE="your_audience"
export OPHELOS_ENVIRONMENT="staging"
export OPHELOS_TENANT_ID="tenant_123"  # Optional for multi-tenant applications
```

```python
import os
from ophelos_sdk import OphelosClient

client = OphelosClient(
    client_id=os.getenv("OPHELOS_CLIENT_ID"),
    client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
    audience=os.getenv("OPHELOS_AUDIENCE"),
    environment=os.getenv("OPHELOS_ENVIRONMENT", "staging"),
    tenant_id=os.getenv("OPHELOS_TENANT_ID")  # Will be None if not set
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
client = OphelosClient(
    client_id="your_client_id",           # Required: OAuth2 client ID
    client_secret="your_client_secret",   # Required: OAuth2 client secret
    audience="your_audience",             # Required: API audience/identifier
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

Test your connection:

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
``` 