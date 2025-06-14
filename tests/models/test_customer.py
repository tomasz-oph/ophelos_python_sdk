"""
Unit tests for Customer model.
"""

import pytest
from datetime import datetime

from ophelos_sdk.models import Customer


class TestCustomerModel:
    """Test cases for Customer model."""

    def test_customer_creation(self, sample_customer_data):
        """Test customer model creation with valid data."""
        customer = Customer(**sample_customer_data)

        assert customer.id == sample_customer_data["id"]
        assert customer.object == "customer"
        assert customer.kind == sample_customer_data["kind"]
        assert customer.full_name == sample_customer_data["full_name"]
        assert customer.first_name == sample_customer_data["first_name"]
        assert customer.last_name == sample_customer_data["last_name"]
        assert customer.preferred_locale == sample_customer_data["preferred_locale"]
        assert customer.contact_details == sample_customer_data["contact_details"]
        assert customer.debts == sample_customer_data["debts"]

    def test_customer_optional_fields(self):
        """Test customer creation with minimal fields."""
        minimal_data = {
            "id": "cust_123",
            "object": "customer",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": {},
        }

        customer = Customer(**minimal_data)
        assert customer.id == "cust_123"
        assert customer.object == "customer"
        assert customer.kind is None
        assert customer.full_name is None
        assert customer.first_name is None
        assert customer.last_name is None
        assert customer.preferred_locale is None
        assert customer.date_of_birth is None
        assert customer.contact_details is None
        assert customer.debts is None
