"""
Unit tests for Customer model.
"""

import pytest
from datetime import datetime, date

from ophelos_sdk.models import Customer, ContactDetail


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

    def test_customer_to_api_body_basic(self):
        """Test customer to_api_body with basic fields."""
        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            preferred_locale="en-GB",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = customer.to_api_body()

        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body
        assert api_body["first_name"] == "John"
        assert api_body["last_name"] == "Doe"
        assert api_body["preferred_locale"] == "en-GB"

    def test_customer_to_api_body_with_metadata(self):
        """Test customer to_api_body with metadata."""
        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="Jane",
            last_name="Smith",
            kind="individual",
            date_of_birth=date(1990, 5, 15),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"source": "test", "priority": "high"},
        )

        api_body = customer.to_api_body()

        assert api_body["first_name"] == "Jane"
        assert api_body["last_name"] == "Smith"
        assert api_body["kind"] == "individual"
        assert api_body["date_of_birth"] == date(1990, 5, 15)
        assert api_body["metadata"] == {"source": "test", "priority": "high"}

    def test_customer_to_api_body_with_contact_details(self):
        """Test customer to_api_body with nested contact details."""
        contact_detail = ContactDetail(
            id="cd_123",
            object="contact_detail",
            type="email",
            value="john@example.com",
            primary=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            contact_details=[contact_detail],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = customer.to_api_body()

        assert "contact_details" in api_body
        assert len(api_body["contact_details"]) == 1
        contact_data = api_body["contact_details"][0]
        assert "id" not in contact_data
        assert "object" not in contact_data
        assert "created_at" not in contact_data
        assert "updated_at" not in contact_data
        assert contact_data["type"] == "email"
        assert contact_data["value"] == "john@example.com"
        assert contact_data["primary"] is True

    def test_customer_to_api_body_exclude_none_false(self):
        """Test customer to_api_body with exclude_none=False."""
        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            kind=None,
            date_of_birth=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = customer.to_api_body(exclude_none=False)

        assert api_body["first_name"] == "John"
        assert api_body["last_name"] == "Doe"
        assert api_body["kind"] is None
        assert api_body["date_of_birth"] is None

    def test_customer_to_api_body_exclude_none_true(self):
        """Test customer to_api_body with exclude_none=True (default)."""
        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            kind=None,
            date_of_birth=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = customer.to_api_body()

        assert api_body["first_name"] == "John"
        assert api_body["last_name"] == "Doe"
        assert "kind" not in api_body
        assert "date_of_birth" not in api_body

    def test_customer_api_body_fields_configuration(self):
        """Test that customer uses correct __api_body_fields__ configuration."""
        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = customer.to_api_body()
        expected_fields = {
            "kind",
            "full_name",
            "first_name",
            "last_name",
            "preferred_locale",
            "date_of_birth",
            "contact_details",
            "metadata",
        }

        for field in expected_fields:
            if getattr(customer, field, None) is not None:
                assert field in api_body or field in [
                    "kind",
                    "full_name",
                    "preferred_locale",
                    "date_of_birth",
                    "contact_details",
                    "metadata",
                ]

    def test_customer_to_api_body_relationship_handling(self):
        """Test customer to_api_body with debt relationships."""
        customer = Customer(
            id="cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            debts=["debt_123", "debt_456"],  # String IDs should be preserved
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = customer.to_api_body()

        # debts field should not be in API body (not in __api_body_fields__)
        assert "debts" not in api_body
