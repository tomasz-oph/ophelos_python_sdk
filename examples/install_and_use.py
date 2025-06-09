#!/usr/bin/env python3
"""
Example: Installing and using the Ophelos SDK from local distribution.

This example shows how to use the SDK after installing it from the local
distribution files.

First install the SDK:
    pip install dist/ophelos_sdk-1.0.0-py3-none-any.whl

Then run this script to see the SDK in action.
"""

import os
from ophelos import OphelosClient


def main():
    """Demonstrate basic SDK usage."""
    
    print("Ophelos SDK Installation and Usage Example")
    print("=" * 50)
    
    # 1. Initialize client for different environments
    print("\n1. Client Initialization")
    print("-" * 25)
    
    # Development environment (local API server)
    dev_client = OphelosClient(
        client_id="dev_client_id",
        client_secret="dev_client_secret", 
        audience="dev_audience",
        environment="development"
    )
    print(f"✓ Development client: {dev_client.http_client.base_url}")
    
    # Staging environment
    staging_client = OphelosClient(
        client_id="staging_client_id",
        client_secret="staging_client_secret",
        audience="staging_audience", 
        environment="staging"
    )
    print(f"✓ Staging client: {staging_client.http_client.base_url}")
    
    # Production environment
    prod_client = OphelosClient(
        client_id="prod_client_id",
        client_secret="prod_client_secret",
        audience="prod_audience",
        environment="production"
    )
    print(f"✓ Production client: {prod_client.http_client.base_url}")
    
    # 2. Environment variable configuration
    print("\n2. Environment Variable Configuration")
    print("-" * 40)
    
    # Set example environment variables
    os.environ["OPHELOS_CLIENT_ID"] = "env_client_id"
    os.environ["OPHELOS_CLIENT_SECRET"] = "env_client_secret"
    os.environ["OPHELOS_AUDIENCE"] = "env_audience"
    os.environ["OPHELOS_ENVIRONMENT"] = "staging"
    
    env_client = OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
        audience=os.getenv("OPHELOS_AUDIENCE"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "staging")
    )
    print(f"✓ Environment-configured client: {env_client.http_client.base_url}")
    
    # 3. Resource managers availability
    print("\n3. Available Resource Managers")
    print("-" * 32)
    
    client = staging_client  # Use staging for examples
    
    resources = [
        ("debts", "Debt management operations"),
        ("customers", "Customer management operations"),
        ("organisations", "Organisation management operations"),
        ("payments", "Payment management operations"),
        ("invoices", "Invoice management operations"),
        ("webhooks", "Webhook management operations"),
        ("payment_plans", "Payment plan management operations"),
        ("communications", "Communication management operations"),
        ("payouts", "Payout management operations"),
        ("tenants", "Tenant management operations"),
    ]
    
    for resource, description in resources:
        if hasattr(client, resource):
            print(f"✓ client.{resource:<15} - {description}")
        else:
            print(f"✗ client.{resource:<15} - Not available")
    
    # 4. Model imports
    print("\n4. Model Imports")
    print("-" * 16)
    
    try:
        from ophelos import (
            Debt, Customer, Organisation, Payment, Invoice,
            DebtStatus, PaymentStatus, Currency
        )
        print("✓ Core models imported successfully")
        
        # Demonstrate enum usage
        print(f"  - Debt statuses: {list(DebtStatus)[:3]}...")
        print(f"  - Payment statuses: {list(PaymentStatus)[:3]}...")
        print(f"  - Currencies: {list(Currency)}")
        
    except ImportError as e:
        print(f"✗ Model import failed: {e}")
    
    # 5. Webhook utilities
    print("\n5. Webhook Utilities")
    print("-" * 19)
    
    try:
        from ophelos import WebhookHandler, construct_event
        
        handler = WebhookHandler("test_secret")
        print("✓ WebhookHandler initialized successfully")
        print("✓ construct_event function available")
        
    except ImportError as e:
        print(f"✗ Webhook import failed: {e}")
    
    # 6. Exception handling
    print("\n6. Exception Classes")
    print("-" * 19)
    
    try:
        from ophelos import (
            OphelosError, OphelosAPIError, AuthenticationError,
            ValidationError, NotFoundError, RateLimitError
        )
        print("✓ All exception classes imported successfully")
        
    except ImportError as e:
        print(f"✗ Exception import failed: {e}")
    
    # 7. Package information
    print("\n7. Package Information")
    print("-" * 22)
    
    try:
        import ophelos
        print(f"✓ Package version: {ophelos.__version__}")
        print(f"✓ Package author: {ophelos.__author__}")
        
    except AttributeError as e:
        print(f"✗ Package info error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 SDK installation and basic functionality verified!")
    print("\nNext steps:")
    print("1. Get your API credentials from Ophelos")
    print("2. Set environment variables or pass credentials directly")
    print("3. Start making API calls!")
    print("\nSee USAGE.md for comprehensive examples.")


if __name__ == "__main__":
    main() 