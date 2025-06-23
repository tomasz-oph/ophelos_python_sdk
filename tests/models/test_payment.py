"""
Unit tests for Payment model.
"""

import pytest
from datetime import datetime

from ophelos_sdk.models import Payment, PaymentStatus


class TestPaymentModel:
    """Test cases for Payment model."""

    def test_payment_creation(self, sample_payment_data):
        """Test payment model creation with valid data."""
        payment = Payment(**sample_payment_data)

        assert payment.id == sample_payment_data["id"]
        assert payment.amount == sample_payment_data["amount"]
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.debt == sample_payment_data["debt"]

    def test_payment_status_enum(self):
        """Test payment status enumeration."""
        assert PaymentStatus.SUCCEEDED == "succeeded"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.DISPUTED == "disputed"

    def test_payment_to_api_body(self):
        """Test payment to_api_body method."""
        payment = Payment(
            id="pay_123",
            object="payment",
            debt="debt_123",
            status=PaymentStatus.SUCCEEDED,
            transaction_at=datetime.now(),
            transaction_ref="TXN-123",
            amount=10000,
            currency="GBP",
            payment_provider="stripe",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"gateway_id": "pi_123"},
        )

        api_body = payment.to_api_body()

        # debt should NOT be in API body as it's set by endpoint context
        assert "debt" not in api_body
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # These fields should be in the API body (based on __api_body_fields__)
        assert api_body["transaction_ref"] == "TXN-123"
        assert api_body["amount"] == 10000
        assert api_body["currency"] == "GBP"
        assert api_body["metadata"] == {"gateway_id": "pi_123"}

        # These fields are NOT in __api_body_fields__ so should be excluded
        assert "status" not in api_body
        assert "payment_provider" not in api_body
        assert "payment_plan" not in api_body

    def test_payment_to_api_body_minimal(self):
        """Test payment to_api_body with minimal fields."""
        payment = Payment(
            id="pay_123",
            object="payment",
            debt="debt_123",
            status=PaymentStatus.PENDING,
            transaction_at=datetime.now(),
            amount=5000,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = payment.to_api_body()

        assert "debt" not in api_body
        assert api_body["amount"] == 5000
        # status is not in __api_body_fields__
        assert "status" not in api_body
        # None values should be excluded by default
        assert "transaction_ref" not in api_body
        assert "currency" not in api_body
