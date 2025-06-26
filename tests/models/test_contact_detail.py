"""
Unit tests for ContactDetail model.
"""

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
            "usage": "permanent",
            "source": "client",
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
        assert contact_detail.usage == "permanent"
        assert contact_detail.source == "client"
        assert contact_detail.status == "active"
        assert contact_detail.metadata == {"custom_field": "value"}

    def test_contact_detail_minimal_fields(self):
        """Test contact detail creation with minimal required fields."""
        minimal_data = {
            "id": "cd_456",
            "object": "contact_detail",
            "type": "phone_number",
            "value": "+44123456789",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        contact_detail = ContactDetail(**minimal_data)
        assert contact_detail.id == "cd_456"
        assert contact_detail.type == ContactDetailType.PHONE_NUMBER
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
            usage="permanent",
            source="client",
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
        assert api_body["usage"] == "permanent"
        assert api_body["source"] == "client"
        assert api_body["status"] == "verified"
        assert api_body["metadata"] == {"verified_date": "2024-01-01"}
