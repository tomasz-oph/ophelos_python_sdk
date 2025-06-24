"""
Unit tests for Organisation model and PaymentOptionsConfiguration.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from ophelos_sdk.models import Organisation, PaymentOptionsConfiguration, ContactDetail, ContactDetailType


class TestPaymentOptionsConfiguration:
    """Test cases for PaymentOptionsConfiguration model."""

    def test_payment_options_configuration_creation(self):
        """Test payment options configuration creation with all fields."""
        config = PaymentOptionsConfiguration(
            pay_later_permitted=True, payment_plans_permitted=False, metadata={"source": "api", "version": "1.0"}
        )

        assert config.pay_later_permitted is True
        assert config.payment_plans_permitted is False
        assert config.metadata == {"source": "api", "version": "1.0"}

    def test_payment_options_configuration_minimal_creation(self):
        """Test payment options configuration creation with minimal fields."""
        config = PaymentOptionsConfiguration()

        assert config.pay_later_permitted is None
        assert config.payment_plans_permitted is None
        assert config.metadata is None

    def test_payment_options_configuration_partial_fields(self):
        """Test payment options configuration with partial fields."""
        config = PaymentOptionsConfiguration(pay_later_permitted=True, metadata={"enabled": True})

        assert config.pay_later_permitted is True
        assert config.payment_plans_permitted is None
        assert config.metadata == {"enabled": True}


class TestOrganisation:
    """Test cases for Organisation model."""

    def test_organisation_creation_minimal(self):
        """Test organisation creation with minimal fields."""
        org = Organisation()

        assert org.id is None
        assert org.object == "organisation"
        assert org.name is None
        assert org.internal_name is None
        assert org.customer_facing_name is None
        assert org.contact_details is None
        assert org.configurations == {}
        assert org.deleted_at is None
        assert org.created_at is None
        assert org.updated_at is None
        assert org.metadata is None
        assert org.payment_options_configuration is None

    def test_organisation_creation_with_basic_fields(self):
        """Test organisation creation with basic fields."""
        org = Organisation(
            id="org_123",
            name="Test Organisation Ltd",
            internal_name="test_org",
            customer_facing_name="Test Org",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert org.id == "org_123"
        assert org.object == "organisation"
        assert org.name == "Test Organisation Ltd"
        assert org.internal_name == "test_org"
        assert org.customer_facing_name == "Test Org"
        assert isinstance(org.created_at, datetime)
        assert isinstance(org.updated_at, datetime)

    def test_organisation_creation_with_all_fields(self):
        """Test organisation creation with all fields."""
        payment_config = PaymentOptionsConfiguration(
            pay_later_permitted=True, payment_plans_permitted=True, metadata={"config_version": "2.0"}
        )

        contact_detail = ContactDetail(type=ContactDetailType.EMAIL, value="contact@testorg.com", primary=True)

        org = Organisation(
            id="org_456",
            object="organisation",
            name="Complete Test Organisation",
            internal_name="complete_test_org",
            customer_facing_name="Complete Test",
            contact_details=[contact_detail],
            configurations={"feature_flags": {"new_ui": True}},
            deleted_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"industry": "fintech", "size": "medium"},
            payment_options_configuration=payment_config,
        )

        assert org.id == "org_456"
        assert org.name == "Complete Test Organisation"
        assert org.internal_name == "complete_test_org"
        assert org.customer_facing_name == "Complete Test"
        assert len(org.contact_details) == 1
        assert isinstance(org.contact_details[0], ContactDetail)
        assert org.configurations == {"feature_flags": {"new_ui": True}}
        assert org.metadata == {"industry": "fintech", "size": "medium"}
        assert isinstance(org.payment_options_configuration, PaymentOptionsConfiguration)
        assert org.payment_options_configuration.pay_later_permitted is True

    def test_organisation_with_contact_detail_ids(self):
        """Test organisation with contact details as string IDs."""
        org = Organisation(
            id="org_789",
            name="String Contact Org",
            contact_details=["cd_123", "cd_456"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert org.contact_details == ["cd_123", "cd_456"]
        assert all(isinstance(cd, str) for cd in org.contact_details)

    def test_organisation_with_mixed_contact_details(self):
        """Test organisation with mixed contact details (objects and IDs)."""
        contact_detail = ContactDetail(type=ContactDetailType.PHONE_NUMBER, value="+44123456789", primary=True)

        org = Organisation(
            id="org_mixed",
            name="Mixed Contact Org",
            contact_details=[contact_detail, "cd_existing_123"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert len(org.contact_details) == 2
        assert isinstance(org.contact_details[0], ContactDetail)
        assert isinstance(org.contact_details[1], str)
        assert org.contact_details[1] == "cd_existing_123"

    def test_organisation_to_api_body_basic(self):
        """Test organisation to_api_body with basic fields."""
        org = Organisation(
            id="org_api_basic",
            object="organisation",
            name="API Test Organisation",
            internal_name="api_test_org",
            customer_facing_name="API Test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = org.to_api_body()

        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body
        assert "deleted_at" not in api_body

        # API body fields should be included
        assert api_body["name"] == "API Test Organisation"
        assert api_body["internal_name"] == "api_test_org"
        assert api_body["customer_facing_name"] == "API Test"

    def test_organisation_to_api_body_with_configurations(self):
        """Test organisation to_api_body with configurations and metadata."""
        org = Organisation(
            id="org_config",
            name="Config Test Org",
            configurations={"notifications": {"email": True, "sms": False}},
            metadata={"region": "EU", "tier": "premium"},
        )

        api_body = org.to_api_body()

        assert api_body["name"] == "Config Test Org"
        assert api_body["configurations"] == {"notifications": {"email": True, "sms": False}}
        assert api_body["metadata"] == {"region": "EU", "tier": "premium"}

    def test_organisation_to_api_body_with_contact_details(self):
        """Test organisation to_api_body with contact details."""
        contact_detail = ContactDetail(
            id="cd_nested", type=ContactDetailType.EMAIL, value="nested@test.com", primary=True
        )

        org = Organisation(
            id="org_contacts", name="Contact Test Org", contact_details=[contact_detail, "cd_existing_456"]
        )

        api_body = org.to_api_body()

        assert api_body["name"] == "Contact Test Org"
        assert "contact_details" in api_body
        assert len(api_body["contact_details"]) == 2

        # First contact detail should be processed as nested object
        nested_contact = api_body["contact_details"][0]
        assert isinstance(nested_contact, dict)
        assert nested_contact["type"] == "email"
        assert nested_contact["value"] == "nested@test.com"
        assert "id" not in nested_contact  # Server fields excluded from nested objects

        # Second contact detail should remain as string ID
        assert api_body["contact_details"][1] == "cd_existing_456"

    def test_organisation_to_api_body_exclude_none_default(self):
        """Test organisation to_api_body excludes None values by default."""
        org = Organisation(name="Minimal Org", internal_name=None, customer_facing_name=None, metadata=None)

        api_body = org.to_api_body()

        assert api_body["name"] == "Minimal Org"
        # None values should be excluded
        assert "internal_name" not in api_body
        assert "customer_facing_name" not in api_body
        assert "metadata" not in api_body

    def test_organisation_to_api_body_include_none(self):
        """Test organisation to_api_body includes None values when exclude_none=False."""
        org = Organisation(name="Include None Org", internal_name=None, customer_facing_name=None, metadata=None)

        api_body = org.to_api_body(exclude_none=False)

        assert api_body["name"] == "Include None Org"
        # None values should be included
        assert "internal_name" in api_body
        assert api_body["internal_name"] is None
        assert "customer_facing_name" in api_body
        assert api_body["customer_facing_name"] is None
        assert "metadata" in api_body
        assert api_body["metadata"] is None

    def test_organisation_with_payment_options_configuration(self):
        """Test organisation with nested payment options configuration."""
        payment_config = PaymentOptionsConfiguration(
            pay_later_permitted=True, payment_plans_permitted=False, metadata={"version": "1.2"}
        )

        org = Organisation(
            id="org_payment_config",
            name="Payment Config Org",
            payment_options_configuration=payment_config,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert isinstance(org.payment_options_configuration, PaymentOptionsConfiguration)
        assert org.payment_options_configuration.pay_later_permitted is True
        assert org.payment_options_configuration.payment_plans_permitted is False
        assert org.payment_options_configuration.metadata == {"version": "1.2"}

        # payment_options_configuration should not be in API body (not in __api_body_fields__)
        api_body = org.to_api_body()
        assert "payment_options_configuration" not in api_body

    def test_organisation_empty_configurations_dict(self):
        """Test organisation with empty configurations dict."""
        org = Organisation(name="Empty Config Org", configurations={})

        assert org.configurations == {}

        api_body = org.to_api_body()
        assert api_body["configurations"] == {}

    def test_organisation_default_configurations(self):
        """Test organisation uses default empty configurations dict."""
        org = Organisation(name="Default Config Org")

        assert org.configurations == {}
        assert isinstance(org.configurations, dict)


class TestOrganisationIntegration:
    """Integration tests for Organisation model with other models."""

    def test_organisation_in_debt_context(self):
        """Test organisation model when used in debt context."""
        # This tests the scenario where Organisation is used as a nested object in Debt
        org = Organisation(
            id="org_debt_context", name="Debt Context Org", created_at=datetime.now(), updated_at=datetime.now()
        )

        # Simulate how it would be used in debt.to_api_body()
        # When org has a real ID, it should be converted to ID reference
        assert org.id == "org_debt_context"
        assert not org.id.startswith("temp_")

        # When org has temp ID, it should be included as full object
        temp_org = Organisation(
            id="temp_org_123", name="Temp Org", created_at=datetime.now(), updated_at=datetime.now()
        )

        assert temp_org.id.startswith("temp_")

    def test_organisation_contact_details_processing(self):
        """Test organisation contact details processing for API body."""
        # Test with mix of ContactDetail objects and string IDs
        contact_obj = ContactDetail(type=ContactDetailType.EMAIL, value="api@test.com")

        org = Organisation(name="Contact Processing Org", contact_details=[contact_obj, "cd_string_123"])

        api_body = org.to_api_body()

        assert len(api_body["contact_details"]) == 2

        # First should be processed as nested object
        assert isinstance(api_body["contact_details"][0], dict)
        assert api_body["contact_details"][0]["type"] == "email"

        # Second should remain as string
        assert api_body["contact_details"][1] == "cd_string_123"
