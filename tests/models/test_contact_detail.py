"""
Unit tests for ContactDetail model.
"""

import pytest
from datetime import datetime

from ophelos_sdk.models import ContactDetail, ContactDetailType


class TestContactDetailModel:
    """Test cases for ContactDetail model."""

    def test_contact_detail_creation(self):
        """Test contact detail model creation with all fields."""
        contact_detail_data = {
            "id": "cd_123",
            "object": "contact_detail",
            "type": "email",
            "value": "test@example.com",
            "primary": True,
            "usage": "billing",
            "source": "manual",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {"custom_field": "value"},
        }

        contact_detail = ContactDetail(**contact_detail_data)

        assert contact_detail.id == "cd_123"
        assert contact_detail.object == "contact_detail"
        assert contact_detail.type == ContactDetailType.EMAIL
        assert contact_detail.value == "test@example.com"
        assert contact_detail.primary is True
        assert contact_detail.usage == "billing"
        assert contact_detail.source == "manual"
        assert contact_detail.status == "active"
        assert contact_detail.metadata == {"custom_field": "value"}

    def test_contact_detail_minimal_fields(self):
        """Test contact detail creation with minimal required fields."""
        minimal_data = {
            "id": "cd_456",
            "object": "contact_detail",
            "type": "phone",
            "value": "+44123456789",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        contact_detail = ContactDetail(**minimal_data)
        assert contact_detail.id == "cd_456"
        assert contact_detail.type == ContactDetailType.PHONE
        assert contact_detail.value == "+44123456789"
        assert contact_detail.primary is None
        assert contact_detail.usage is None
        assert contact_detail.source is None
        assert contact_detail.status is None
        assert contact_detail.metadata is None

    def test_contact_detail_to_api_body(self):
        """Test contact detail to_api_body method."""
        contact_detail = ContactDetail(
            id="cd_123",
            object="contact_detail",
            type="email",
            value="test@example.com",
            primary=True,
            usage="billing",
            source="user_input",
            status="verified",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"verified_date": "2024-01-01"},
        )

        api_body = contact_detail.to_api_body()

        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # API body fields should be included
        assert api_body["type"] == "email"
        assert api_body["value"] == "test@example.com"
        assert api_body["primary"] is True
        assert api_body["usage"] == "billing"
        assert api_body["source"] == "user_input"
        assert api_body["status"] == "verified"
        assert api_body["metadata"] == {"verified_date": "2024-01-01"}

    def test_contact_detail_to_api_body_minimal(self):
        """Test contact detail to_api_body with minimal fields."""
        contact_detail = ContactDetail(
            id="cd_456",
            object="contact_detail",
            type="phone",
            value="+44123456789",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = contact_detail.to_api_body()

        assert api_body["type"] == "phone"
        assert api_body["value"] == "+44123456789"
        # None values should be excluded by default
        assert "primary" not in api_body
        assert "usage" not in api_body
        assert "source" not in api_body
        assert "status" not in api_body
        assert "metadata" not in api_body
