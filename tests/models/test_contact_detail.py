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