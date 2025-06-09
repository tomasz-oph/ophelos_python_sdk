"""
Unit tests for Ophelos SDK models.
"""

import pytest
from datetime import datetime, date

from ophelos.models import (
    Debt, Customer, Payment, Invoice, Organisation,
    DebtStatus, PaymentStatus, Currency, ContactDetailType,
    PaginatedResponse, WebhookEvent
)


class TestDebtModel:
    """Test cases for Debt model."""

    def test_debt_creation(self, sample_debt_data):
        """Test debt model creation with valid data."""
        debt = Debt(**sample_debt_data)
        
        assert debt.id == sample_debt_data["id"]
        assert debt.total_amount == sample_debt_data["total_amount"]
        assert debt.status == DebtStatus.PREPARED
        assert debt.currency == Currency.GBP
        assert debt.customer_id == sample_debt_data["customer_id"]
        assert debt.organisation_id == sample_debt_data["organisation_id"]
        assert debt.metadata == sample_debt_data["metadata"]

    def test_debt_status_enum(self):
        """Test debt status enumeration."""
        assert DebtStatus.PREPARED == "prepared"
        assert DebtStatus.ANALYZING == "analyzing"
        assert DebtStatus.CLOSED == "closed"
        assert DebtStatus.WITHDRAWN == "withdrawn"

    def test_debt_optional_fields(self):
        """Test debt creation with minimal required fields."""
        minimal_data = {
            "id": "debt_123",
            "object": "debt",
            "total_amount": 10000,
            "status": "prepared",
            "customer_id": "cust_123",
            "organisation_id": "org_123",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        debt = Debt(**minimal_data)
        assert debt.id == "debt_123"
        assert debt.account_number is None
        assert debt.reference_code is None
        assert debt.metadata is None


class TestCustomerModel:
    """Test cases for Customer model."""

    def test_customer_creation(self, sample_customer_data):
        """Test customer model creation with valid data."""
        customer = Customer(**sample_customer_data)
        
        assert customer.id == sample_customer_data["id"]
        assert customer.first_name == sample_customer_data["first_name"]
        assert customer.last_name == sample_customer_data["last_name"]
        assert customer.organisation_id == sample_customer_data["organisation_id"]

    def test_customer_optional_fields(self):
        """Test customer creation with minimal fields."""
        minimal_data = {
            "id": "cust_123",
            "object": "customer",
            "organisation_id": "org_123",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        customer = Customer(**minimal_data)
        assert customer.id == "cust_123"
        assert customer.first_name is None
        assert customer.last_name is None
        assert customer.date_of_birth is None


class TestPaymentModel:
    """Test cases for Payment model."""

    def test_payment_creation(self, sample_payment_data):
        """Test payment model creation with valid data."""
        payment = Payment(**sample_payment_data)
        
        assert payment.id == sample_payment_data["id"]
        assert payment.amount == sample_payment_data["amount"]
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.debt_id == sample_payment_data["debt_id"]
        assert payment.organisation_id == sample_payment_data["organisation_id"]

    def test_payment_status_enum(self):
        """Test payment status enumeration."""
        assert PaymentStatus.SUCCEEDED == "succeeded"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.DISPUTED == "disputed"


class TestEnumerations:
    """Test cases for enumeration types."""

    def test_currency_enum(self):
        """Test currency enumeration."""
        assert Currency.GBP == "GBP"
        assert Currency.EUR == "EUR"
        assert Currency.USD == "USD"

    def test_contact_detail_type_enum(self):
        """Test contact detail type enumeration."""
        assert ContactDetailType.EMAIL == "email"
        assert ContactDetailType.PHONE == "phone"
        assert ContactDetailType.MOBILE == "mobile"
        assert ContactDetailType.ADDRESS == "address"


class TestPaginatedResponse:
    """Test cases for paginated response model."""

    def test_empty_paginated_response(self):
        """Test empty paginated response."""
        response = PaginatedResponse(data=[])
        
        assert response.object == "list"
        assert response.data == []
        assert response.has_more is False
        assert response.total_count is None

    def test_paginated_response_with_data(self, sample_debt_data):
        """Test paginated response with data."""
        response_data = {
            "object": "list",
            "data": [sample_debt_data],
            "has_more": True,
            "total_count": 10
        }
        
        response = PaginatedResponse(**response_data)
        assert len(response.data) == 1
        assert response.has_more is True
        assert response.total_count == 10


class TestWebhookEvent:
    """Test cases for webhook event model."""

    def test_webhook_event_creation(self, sample_webhook_event):
        """Test webhook event creation."""
        event = WebhookEvent(**sample_webhook_event)
        
        assert event.id == sample_webhook_event["id"]
        assert event.type == sample_webhook_event["type"]
        assert event.data == sample_webhook_event["data"]
        assert event.livemode is False

    def test_webhook_event_types(self):
        """Test common webhook event types."""
        event_types = [
            "debt.created",
            "debt.updated", 
            "debt.closed",
            "payment.succeeded",
            "payment.failed",
            "customer.created"
        ]
        
        for event_type in event_types:
            event_data = {
                "id": "evt_123",
                "object": "event",
                "type": event_type,
                "created_at": datetime.now().isoformat(),
                "livemode": False,
                "data": {"test": "data"}
            }
            
            event = WebhookEvent(**event_data)
            assert event.type == event_type


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_debt_json_serialization(self, sample_debt_data):
        """Test debt model JSON serialization."""
        debt = Debt(**sample_debt_data)
        
        # Convert to dict (similar to JSON serialization)
        debt_dict = debt.model_dump()
        
        assert debt_dict["id"] == sample_debt_data["id"]
        assert debt_dict["total_amount"] == sample_debt_data["total_amount"]
        assert debt_dict["status"] == sample_debt_data["status"]

    def test_model_extra_fields(self):
        """Test that models accept extra fields (for API compatibility)."""
        debt_data = {
            "id": "debt_123",
            "object": "debt",
            "total_amount": 10000,
            "status": "prepared",
            "customer_id": "cust_123",
            "organisation_id": "org_123",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "unknown_field": "should_be_accepted"  # Extra field
        }
        
        # Should not raise an error due to extra="allow" in BaseOphelosModel
        debt = Debt(**debt_data)
        assert debt.id == "debt_123"
        # Extra field should be accessible
        assert hasattr(debt, 'unknown_field')
        assert debt.unknown_field == "should_be_accepted" 