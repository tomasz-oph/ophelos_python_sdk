#!/usr/bin/env python3
"""
Test script to validate Ophelos SDK installation and basic functionality.
"""

import sys
import traceback


def test_imports():
    """Test that all main components can be imported."""
    print("Testing imports...")
    try:
        # Test main client import
        from ophelos import OphelosClient

        print("✓ OphelosClient imported successfully")

        # Test exception imports
        from ophelos import (
            AuthenticationError,
            NotFoundError,
            OphelosAPIError,
            OphelosError,
            RateLimitError,
            ValidationError,
        )

        print("✓ Exception classes imported successfully")

        # Test model imports
        from ophelos import Customer, Debt, DebtStatus, Invoice, Organisation, Payment, PaymentStatus, WebhookEvent

        print("✓ Model classes imported successfully")

        # Test webhook imports
        from ophelos import WebhookHandler, construct_event

        print("✓ Webhook utilities imported successfully")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        traceback.print_exc()
        return False


def test_client_initialization():
    """Test client initialization without making API calls."""
    print("\nTesting client initialization...")
    try:
        from ophelos import OphelosClient

        # Test initialization (should not make any API calls)
        client = OphelosClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            audience="test_audience",
            environment="staging",
        )
        print("✓ Client initialized successfully")

        # Test that resource managers are available
        assert hasattr(client, "debts"), "Missing debts resource"
        assert hasattr(client, "customers"), "Missing customers resource"
        assert hasattr(client, "payments"), "Missing payments resource"
        assert hasattr(client, "organisations"), "Missing organisations resource"
        assert hasattr(client, "invoices"), "Missing invoices resource"
        assert hasattr(client, "webhooks"), "Missing webhooks resource"
        print("✓ All resource managers available")

        return True
    except Exception as e:
        print(f"✗ Client initialization error: {e}")
        traceback.print_exc()
        return False


def test_models():
    """Test model creation and validation."""
    print("\nTesting models...")
    try:
        from datetime import datetime

        from ophelos import Customer, Debt, DebtStatus, Payment, PaymentStatus

        # Test debt status enum
        status = DebtStatus.PREPARED
        assert status == "prepared", f"Unexpected status value: {status}"
        print("✓ DebtStatus enum working correctly")

        # Test payment status enum
        payment_status = PaymentStatus.SUCCEEDED
        assert payment_status == "succeeded", f"Unexpected payment status: {payment_status}"
        print("✓ PaymentStatus enum working correctly")

        # Test model creation (basic structure test)
        sample_debt_data = {
            "id": "debt_123",
            "object": "debt",
            "total_amount": 10000,
            "status": "prepared",
            "customer_id": "cust_123",
            "organisation_id": "org_123",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        debt = Debt(**sample_debt_data)
        assert debt.id == "debt_123"
        assert debt.total_amount == 10000
        print("✓ Debt model creation working correctly")

        return True
    except Exception as e:
        print(f"✗ Model testing error: {e}")
        traceback.print_exc()
        return False


def test_webhook_handler():
    """Test webhook handler functionality."""
    print("\nTesting webhook handler...")
    try:
        import json

        from ophelos import WebhookHandler

        # Initialize webhook handler
        handler = WebhookHandler("test_secret")
        print("✓ WebhookHandler initialized successfully")

        # Test event parsing (without signature verification)
        sample_event = {
            "id": "evt_123",
            "object": "event",
            "type": "debt.created",
            "created_at": "2024-01-15T10:00:00Z",
            "livemode": False,
            "data": {"id": "debt_123", "object": "debt"},
        }

        event = handler.parse_event(json.dumps(sample_event))
        assert event.id == "evt_123"
        assert event.type == "debt.created"
        print("✓ Webhook event parsing working correctly")

        return True
    except Exception as e:
        print(f"✗ Webhook handler testing error: {e}")
        traceback.print_exc()
        return False


def test_version_info():
    """Test version and package info."""
    print("\nTesting package information...")
    try:
        import ophelos

        assert hasattr(ophelos, "__version__"), "Missing version info"
        assert hasattr(ophelos, "__author__"), "Missing author info"

        print(f"✓ Package version: {ophelos.__version__}")
        print(f"✓ Package author: {ophelos.__author__}")

        return True
    except Exception as e:
        print(f"✗ Version info error: {e}")
        return False


def main():
    """Run all tests."""
    print("Ophelos SDK Installation Test")
    print("=" * 40)

    tests = [
        test_imports,
        test_client_initialization,
        test_models,
        test_webhook_handler,
        test_version_info,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")

    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! The Ophelos SDK is properly installed and working.")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
