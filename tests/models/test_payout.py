"""
Unit tests for Payout model.
"""

import pytest
from datetime import datetime, date

from ophelos_sdk.models import Payout, Currency


class TestPayout:
    """Test cases for Payout model."""

    def test_payout_creation_minimal(self):
        """Test payout creation with minimal required fields."""
        payout = Payout(amount=50000)
        
        assert payout.id is None
        assert payout.object == "payout"
        assert payout.amount == 50000
        assert payout.currency is None
        assert payout.status is None
        assert payout.payout_date is None
        assert payout.organisation_id is None
        assert payout.metadata is None
        assert payout.created_at is None
        assert payout.updated_at is None

    def test_payout_creation_with_all_fields(self):
        """Test payout creation with all fields."""
        payout_date = date(2024, 4, 15)
        created_time = datetime.now()
        updated_time = datetime.now()
        
        payout = Payout(
            id="payout_123",
            object="payout",
            amount=75000,
            currency=Currency.GBP,
            status="pending",
            payout_date=payout_date,
            organisation_id="org_456",
            metadata={"batch_id": "batch_001", "region": "UK"},
            created_at=created_time,
            updated_at=updated_time
        )
        
        assert payout.id == "payout_123"
        assert payout.object == "payout"
        assert payout.amount == 75000
        assert payout.currency == Currency.GBP
        assert payout.status == "pending"
        assert payout.payout_date == payout_date
        assert payout.organisation_id == "org_456"
        assert payout.metadata == {"batch_id": "batch_001", "region": "UK"}
        assert payout.created_at == created_time
        assert payout.updated_at == updated_time

    def test_payout_with_currency_enum(self):
        """Test payout creation with Currency enum."""
        payout = Payout(
            amount=100000,
            currency=Currency.EUR,
            status="completed",
            organisation_id="org_789"
        )
        
        assert payout.amount == 100000
        assert payout.currency == Currency.EUR
        assert payout.status == "completed"
        assert payout.organisation_id == "org_789"

    def test_payout_with_currency_string(self):
        """Test payout creation with currency as string."""
        payout = Payout(
            amount=25000,
            currency="USD",
            status="failed",
            payout_date=date(2024, 5, 1)
        )
        
        assert payout.amount == 25000
        assert payout.currency == "USD"
        assert payout.status == "failed"
        assert payout.payout_date == date(2024, 5, 1)

    def test_payout_to_api_body_basic(self):
        """Test payout to_api_body with basic fields."""
        payout = Payout(
            id="payout_api_test",
            object="payout",
            amount=60000,
            currency=Currency.GBP,
            status="processing",
            payout_date=date(2024, 6, 1),
            organisation_id="org_api_test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"priority": "high"}
        )
        
        api_body = payout.to_api_body()
        
        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body
        
        # Status is typically server-managed, so might not be in API body
        # But amount, currency, payout_date, organisation_id, metadata should be included
        assert api_body["amount"] == 60000
        assert api_body["currency"] == "GBP"  # Enum serialized as string
        assert api_body["payout_date"] == "2024-06-01"  # Date serialized as ISO string
        assert api_body["organisation_id"] == "org_api_test"
        assert api_body["metadata"] == {"priority": "high"}

    def test_payout_to_api_body_minimal(self):
        """Test payout to_api_body with minimal fields."""
        payout = Payout(
            id="payout_minimal",
            amount=30000,
            organisation_id="org_minimal"
        )
        
        api_body = payout.to_api_body()
        
        assert api_body["amount"] == 30000
        assert api_body["organisation_id"] == "org_minimal"
        # None values should be excluded by default
        assert "currency" not in api_body
        assert "payout_date" not in api_body
        assert "metadata" not in api_body

    def test_payout_to_api_body_exclude_none_false(self):
        """Test payout to_api_body includes None values when exclude_none=False."""
        payout = Payout(
            amount=40000,
            currency=None,
            payout_date=None,
            organisation_id="org_include_none",
            metadata=None
        )
        
        api_body = payout.to_api_body(exclude_none=False)
        
        assert api_body["amount"] == 40000
        assert api_body["organisation_id"] == "org_include_none"
        # None values should be included
        assert "currency" in api_body
        assert api_body["currency"] is None
        assert "payout_date" in api_body
        assert api_body["payout_date"] is None
        assert "metadata" in api_body
        assert api_body["metadata"] is None

    def test_payout_date_serialization_in_api_body(self):
        """Test that date fields are properly serialized in to_api_body."""
        payout_date = date(2024, 7, 15)
        
        payout = Payout(
            amount=80000,
            currency=Currency.USD,
            payout_date=payout_date,
            organisation_id="org_date_test"
        )
        
        api_body = payout.to_api_body()
        
        # Date should be serialized as ISO format string
        assert api_body["payout_date"] == "2024-07-15"
        assert isinstance(api_body["payout_date"], str)

    def test_payout_api_body_excludes_server_fields(self):
        """Test that payout API body excludes all server-generated fields."""
        payout = Payout(
            id="payout_server_test",
            object="payout",
            amount=90000,
            currency=Currency.EUR,
            status="completed",
            organisation_id="org_server_test",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        api_body = payout.to_api_body()
        
        server_fields = {"id", "object", "created_at", "updated_at"}
        for field in server_fields:
            assert field not in api_body

    def test_payout_large_amounts(self):
        """Test payout with large amounts (edge case)."""
        large_amount = 999999999  # Large amount in cents
        
        payout = Payout(
            amount=large_amount,
            currency=Currency.GBP,
            organisation_id="org_large_amount"
        )
        
        assert payout.amount == large_amount
        
        api_body = payout.to_api_body()
        assert api_body["amount"] == large_amount

    def test_payout_status_values(self):
        """Test payout with different status values."""
        statuses = ["pending", "processing", "completed", "failed", "cancelled"]
        
        for status in statuses:
            payout = Payout(
                amount=50000,
                status=status,
                organisation_id=f"org_{status}"
            )
            
            assert payout.status == status
            assert payout.organisation_id == f"org_{status}" 