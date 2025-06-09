#!/usr/bin/env python3
"""
Basic usage example for the Ophelos Python SDK.

This example demonstrates common operations like creating customers,
managing debts, processing payments, and handling webhooks.
"""

import os
from datetime import datetime, date
from ophelos import OphelosClient, WebhookHandler, construct_event
from ophelos.exceptions import OphelosAPIError, AuthenticationError


def main():
    """Main example function."""
    
    # Initialize the client with credentials from environment variables
    client = OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
        audience=os.getenv("OPHELOS_AUDIENCE"),
        environment="staging"  # Use "production" for live environment
    )
    
    try:
        # Test connection
        print("Testing API connection...")
        if client.test_connection():
            print("✓ Connected to Ophelos API successfully")
        else:
            print("✗ Failed to connect to Ophelos API")
            return
        
        # Example 1: Create a customer
        print("\n--- Creating a customer ---")
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "organisation_id": "org_example123",  # Replace with actual org ID
            "metadata": {
                "external_id": "customer_001",
                "source": "example_script"
            }
        }
        
        customer = client.customers.create(customer_data)
        print(f"Created customer: {customer.id} - {customer.first_name} {customer.last_name}")
        
        # Example 2: Create a debt for the customer
        print("\n--- Creating a debt ---")
        debt_data = {
            "customer_id": customer.id,
            "organisation_id": "org_example123",  # Replace with actual org ID
            "total_amount": 10000,  # £100.00 in pence
            "currency": "GBP",
            "reference_code": f"DEBT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "account_number": "ACC-001",
            "start_at": date.today().isoformat(),
            "metadata": {
                "case_id": "12345",
                "original_creditor": "Example Corp"
            }
        }
        
        debt = client.debts.create(debt_data)
        print(f"Created debt: {debt.id} - £{debt.total_amount / 100:.2f}")
        
        # Example 3: Mark debt as ready for processing
        print("\n--- Preparing debt for processing ---")
        prepared_debt = client.debts.ready(debt.id)
        print(f"Debt status: {prepared_debt.status}")
        
        # Example 4: List debts with filtering
        print("\n--- Listing debts ---")
        debts = client.debts.list(limit=5, expand=["customer"])
        print(f"Found {len(debts.data)} debts")
        for debt_item in debts.data:
            print(f"  - {debt_item['id']}: £{debt_item['total_amount'] / 100:.2f} ({debt_item['status']})")
        
        # Example 5: Search customers
        print("\n--- Searching customers ---")
        results = client.customers.search("first_name:John", limit=3)
        print(f"Found {len(results.data)} customers named John")
        
        # Example 6: Create an external payment
        print("\n--- Recording external payment ---")
        payment_data = {
            "amount": 5000,  # £50.00 in pence
            "transaction_at": datetime.now().isoformat(),
            "payment_provider": "bank_transfer",
            "transaction_ref": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "metadata": {
                "external_reference": "BANK-REF-123"
            }
        }
        
        payment = client.debts.create_payment(debt.id, payment_data)
        print(f"Created payment: {payment.id} - £{payment.amount / 100:.2f}")
        
        # Example 7: Get updated debt with payments
        print("\n--- Getting debt with payments ---")
        updated_debt = client.debts.get(debt.id, expand=["payments", "customer"])
        print(f"Debt {updated_debt.id} now has {len(updated_debt.payments or [])} payments")
        
        # Example 8: List all payments
        print("\n--- Listing payments ---")
        payments = client.payments.list(limit=5)
        print(f"Found {len(payments.data)} payments")
        
        # Example 9: Search payments by status
        print("\n--- Searching successful payments ---")
        successful_payments = client.payments.search("status:succeeded", limit=3)
        print(f"Found {len(successful_payments.data)} successful payments")
        
    except AuthenticationError as e:
        print(f"Authentication error: {e.message}")
        print("Please check your credentials")
    except OphelosAPIError as e:
        print(f"API error: {e.message} (Status: {e.status_code})")
    except Exception as e:
        print(f"Unexpected error: {e}")


def webhook_example():
    """Example of webhook handling."""
    print("\n--- Webhook handling example ---")
    
    # Initialize webhook handler
    webhook_secret = os.getenv("OPHELOS_WEBHOOK_SECRET", "your_webhook_secret")
    webhook_handler = WebhookHandler(webhook_secret)
    
    # Example webhook payload and signature (these would come from Ophelos)
    sample_payload = """{
        "id": "evt_123456789",
        "object": "event",
        "type": "debt.created",
        "created_at": "2024-01-15T10:30:00Z",
        "livemode": false,
        "data": {
            "id": "debt_123",
            "object": "debt",
            "status": "prepared",
            "total_amount": 10000,
            "currency": "GBP"
        }
    }"""
    
    # Note: In a real webhook endpoint, you would get these from the request
    sample_signature = "t=1705315800,v1=sample_signature_hash"
    
    try:
        # Parse the webhook event (signature verification would happen here)
        event = webhook_handler.parse_event(sample_payload)
        print(f"Received webhook event: {event.type}")
        print(f"Event ID: {event.id}")
        print(f"Data object: {event.data}")
        
        # Handle different event types
        if event.type == "debt.created":
            print("A new debt was created!")
        elif event.type == "payment.succeeded":
            print("A payment was successful!")
        else:
            print(f"Received event type: {event.type}")
            
    except Exception as e:
        print(f"Webhook handling error: {e}")


if __name__ == "__main__":
    print("Ophelos Python SDK - Basic Usage Example")
    print("=" * 50)
    
    # Check for required environment variables
    required_vars = ["OPHELOS_CLIENT_ID", "OPHELOS_CLIENT_SECRET", "OPHELOS_AUDIENCE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables and try again.")
        print("Example:")
        print("export OPHELOS_CLIENT_ID='your_client_id'")
        print("export OPHELOS_CLIENT_SECRET='your_client_secret'") 
        print("export OPHELOS_AUDIENCE='your_audience'")
    else:
        main()
        webhook_example()
    
    print("\nExample completed!") 