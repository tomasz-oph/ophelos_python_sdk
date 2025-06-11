"""
Unit tests for Payment model.
"""

import pytest
from datetime import datetime

from ophelos.models import Payment, PaymentStatus


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