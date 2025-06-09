# Ophelos SDK Usage Guide

This guide shows how to install and use the Ophelos SDK from the local distribution files.

## Installation

### Option 1: Install from Wheel (Recommended)

Install directly from the built wheel file:

```bash
pip install dist/ophelos_sdk-1.0.0-py3-none-any.whl
```

### Option 2: Install from Source Distribution

Install from the source distribution:

```bash
pip install dist/ophelos-sdk-1.0.0.tar.gz
```

### Option 3: Development Installation

For development with live changes:

```bash
pip install -e .
```

## Basic Usage

### 1. Initialize the Client

```python
from ophelos import OphelosClient

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
```

### 2. Working with Debts

```python
# List debts
debts = client.debts.list(limit=10)
print(f"Found {len(debts.data)} debts")

# Get a specific debt
debt = client.debts.get("debt_123456789", expand=["customer", "payments"])
print(f"Debt amount: {debt.total_amount} {debt.currency}")

# Search debts
results = client.debts.search("status:paying", limit=20)
for debt in results.data:
    print(f"Debt {debt.id}: {debt.status}")

# Create a new debt
new_debt = client.debts.create({
    "customer_id": "cust_123456789",
    "organisation_id": "org_123456789",
    "total_amount": 10000,  # Amount in cents
    "currency": "GBP",
    "reference_code": "REF-001"
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

### 3. Working with Customers

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
    "organisation_id": "org_123456789",
    "country_code": "GB",
    "postal_code": "SW1A 1AA"
})

# Update customer information
updated_customer = client.customers.update("cust_123456789", {
    "phone": "+447700900123",
    "preferred_locale": "en-GB"
})
```

### 4. Working with Payments

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

### 5. Working with Organisations

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

### 6. Webhook Handling

```python
from ophelos import WebhookHandler, construct_event

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
from ophelos import (
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
```

```python
import os
from ophelos import OphelosClient

client = OphelosClient(
    client_id=os.getenv("OPHELOS_CLIENT_ID"),
    client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
    audience=os.getenv("OPHELOS_AUDIENCE"),
    environment=os.getenv("OPHELOS_ENVIRONMENT", "staging")
)
```

### Timeout and Retry Configuration

```python
client = OphelosClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    audience="your_audience",
    environment="staging",
    timeout=60,  # Request timeout in seconds
    max_retries=5  # Maximum retry attempts
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
        if debt.status == "prepared":
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