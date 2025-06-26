"""
Unit tests for Communication and CommunicationTemplate models.
"""

from datetime import datetime

from ophelos_sdk.models import Communication, CommunicationTemplate, ContactDetail, Debt


class TestCommunicationTemplateModel:
    """Test cases for CommunicationTemplate model."""

    def test_communication_template_creation(self):
        """Test communication template model creation."""
        template_data = {
            "id": "ct_123",
            "object": "communication_template",
            "name": "Payment Reminder Template",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        template = CommunicationTemplate(**template_data)

        assert template.id == "ct_123"
        assert template.object == "communication_template"
        assert template.name == "Payment Reminder Template"


class TestUpdatedCommunicationModel:
    """Test cases for updated Communication model."""

    def test_communication_with_expandable_fields(self):
        """Test communication with all expandable fields."""
        communication_data = {
            "id": "comm_123",
            "object": "communication",
            "debt": {
                "id": "debt_456",
                "object": "debt",
                "status": {
                    "value": "contacted",
                    "whodunnit": "system",
                    "context": None,
                    "reason": None,
                    "updated_at": datetime.now().isoformat(),
                },
                "customer": "cust_789",
                "organisation": "org_101",
                "summary": {"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            "template": {
                "id": "ct_456",
                "object": "communication_template",
                "name": "Final Notice Template",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            "status": "sent",
            "provider": "email_service",
            "provider_reference": "msg_789",
            "direction": "outbound",
            "delivery_method": "email",
            "contact_detail": {
                "id": "cd_789",
                "object": "contact_detail",
                "type": "email",
                "value": "customer@example.com",
                "primary": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {"campaign_id": "camp_123"},
        }

        communication = Communication(**communication_data)

        assert communication.id == "comm_123"
        assert communication.object == "communication"
        assert isinstance(communication.debt, Debt)  # Expanded debt object
        assert communication.debt.id == "debt_456"
        assert isinstance(communication.template, CommunicationTemplate)  # Expanded template object
        assert communication.template.name == "Final Notice Template"
        assert communication.status == "sent"
        assert communication.provider == "email_service"
        assert communication.provider_reference == "msg_789"
        assert communication.direction == "outbound"
        assert communication.delivery_method == "email"
        assert isinstance(communication.contact_detail, ContactDetail)  # Expanded contact detail
        assert communication.contact_detail.value == "customer@example.com"
        assert communication.metadata == {"campaign_id": "camp_123"}

    def test_communication_with_ids_only(self):
        """Test communication with only string IDs for expandable fields."""
        communication_data = {
            "id": "comm_456",
            "object": "communication",
            "debt": "debt_789",
            "template": "ct_789",
            "status": "pending",
            "provider": "sms_gateway",
            "provider_reference": "sms_456",
            "direction": "outbound",
            "contact_detail": "cd_456",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        communication = Communication(**communication_data)

        assert communication.id == "comm_456"
        assert communication.debt == "debt_789"  # String debt ID
        assert communication.template == "ct_789"  # String template ID
        assert communication.status == "pending"
        assert communication.provider == "sms_gateway"
        assert communication.provider_reference == "sms_456"
        assert communication.direction == "outbound"
        assert communication.contact_detail == "cd_456"  # String contact detail ID
        assert communication.delivery_method is None
        assert communication.metadata is None

    def test_communication_with_null_optional_fields(self):
        """Test communication with null optional expandable fields."""
        communication_data = {
            "id": "comm_789",
            "object": "communication",
            "debt": "debt_123",
            "template": None,
            "status": "failed",
            "provider": "email_service",
            "direction": "outbound",
            "contact_detail": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        communication = Communication(**communication_data)

        assert communication.id == "comm_789"
        assert communication.debt == "debt_123"
        assert communication.template is None
        assert communication.status == "failed"
        assert communication.provider == "email_service"
        assert communication.direction == "outbound"
        assert communication.contact_detail is None
        assert communication.provider_reference is None
        assert communication.delivery_method is None
        assert communication.metadata is None
