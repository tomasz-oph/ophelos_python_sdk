"""
Unit tests for Customer model.
"""

import pytest
from datetime import datetime, date

from ophelos_sdk.models import (
    Customer, 
    ContactDetail, 
    ContactDetailType, 
    ContactDetailUsage, 
    ContactDetailSource
)


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
        assert api_body["date_of_birth"] == "1990-05-15"  # Date is serialized as ISO string
        assert api_body["metadata"] == {"source": "test", "priority": "high"}

    def test_customer_to_api_body_with_contact_details(self):
        """Test customer to_api_body with nested contact details."""
        contact_detail = ContactDetail(
            id="cd_123",
            object="contact_detail",
            type=ContactDetailType.EMAIL,
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


class TestContactDetailEnums:
    """Test cases for ContactDetail enums."""

    def test_contact_detail_type_enum(self):
        """Test ContactDetailType enum values."""
        assert ContactDetailType.EMAIL == "email"
        assert ContactDetailType.PHONE_NUMBER == "phone_number"
        assert ContactDetailType.MOBILE_NUMBER == "mobile_number"
        assert ContactDetailType.FAX_NUMBER == "fax_number"
        assert ContactDetailType.ADDRESS == "address"
        
        # Test all enum values are defined
        expected_types = {
            "email", "phone_number", "mobile_number", "fax_number", "address"
        }
        actual_types = {member.value for member in ContactDetailType}
        assert actual_types == expected_types

    def test_contact_detail_usage_enum(self):
        """Test ContactDetailUsage enum values."""
        assert ContactDetailUsage.PERMANENT == "permanent"
        assert ContactDetailUsage.WORK == "work"
        assert ContactDetailUsage.SUPPLY_ADDRESS == "supply_address"
        assert ContactDetailUsage.DELIVERY_ADDRESS == "delivery_address"
        assert ContactDetailUsage.OTHER == "other"
        
        # Test all enum values are defined
        expected_usages = {
            "permanent", "work", "supply_address", "delivery_address", "other"
        }
        actual_usages = {member.value for member in ContactDetailUsage}
        assert actual_usages == expected_usages

    def test_contact_detail_source_enum(self):
        """Test ContactDetailSource enum values."""
        assert ContactDetailSource.CLIENT == "client"
        assert ContactDetailSource.CUSTOMER == "customer"
        assert ContactDetailSource.SUPPORT_AGENT == "support_agent"
        assert ContactDetailSource.OTHER == "other"
        
        # Test all enum values are defined
        expected_sources = {
            "client", "customer", "support_agent", "other"
        }
        actual_sources = {member.value for member in ContactDetailSource}
        assert actual_sources == expected_sources


class TestContactDetailModel:
    """Test cases for ContactDetail model."""

    def test_contact_detail_creation_with_enums(self):
        """Test contact detail creation using enum values."""
        contact = ContactDetail(
            type=ContactDetailType.EMAIL,
            value="test@example.com",
            primary=True,
            usage=ContactDetailUsage.PERMANENT,
            source=ContactDetailSource.CLIENT,
            status="verified"
        )
        
        assert contact.type == ContactDetailType.EMAIL
        assert contact.value == "test@example.com"
        assert contact.primary is True
        assert contact.usage == ContactDetailUsage.PERMANENT
        assert contact.source == ContactDetailSource.CLIENT
        assert contact.status == "verified"

    def test_contact_detail_creation_with_string_values(self):
        """Test contact detail creation using string values."""
        contact = ContactDetail(
            type="mobile_number",
            value="+1234567890",
            primary=False,
            usage="work",
            source="customer",
            status="unverified"
        )
        
        assert contact.type == "mobile_number"
        assert contact.value == "+1234567890"
        assert contact.primary is False
        assert contact.usage == "work"
        assert contact.source == "customer"
        assert contact.status == "unverified"

    def test_contact_detail_minimal_creation(self):
        """Test contact detail creation with only required fields."""
        contact = ContactDetail(
            type=ContactDetailType.PHONE_NUMBER,
            value="+44123456789"
        )
        
        assert contact.type == ContactDetailType.PHONE_NUMBER
        assert contact.value == "+44123456789"
        assert contact.primary is None
        assert contact.usage is None
        assert contact.source is None
        assert contact.status is None


class TestCustomerWithContactDetails:
    """Test cases for Customer model with ContactDetail integration."""

    def test_customer_with_enum_contact_details(self):
        """Test customer creation with contact details using enums."""
        contact1 = ContactDetail(
            type=ContactDetailType.EMAIL,
            value="john@example.com",
            primary=True,
            usage=ContactDetailUsage.PERMANENT,
            source=ContactDetailSource.CLIENT
        )
        
        contact2 = ContactDetail(
            type=ContactDetailType.MOBILE_NUMBER,
            value="+447466123456",
            primary=False,
            usage=ContactDetailUsage.WORK,
            source=ContactDetailSource.CUSTOMER
        )
        
        customer = Customer(
            first_name="John",
            last_name="Doe",
            contact_details=[contact1, contact2]
        )
        
        assert len(customer.contact_details) == 2
        assert customer.contact_details[0].type == ContactDetailType.EMAIL
        assert customer.contact_details[1].type == ContactDetailType.MOBILE_NUMBER

    def test_customer_to_api_body_with_enum_contact_details(self):
        """Test customer to_api_body with contact details using enums."""
        contact = ContactDetail(
            type=ContactDetailType.EMAIL,
            value="john@example.com",
            primary=True,
            usage=ContactDetailUsage.PERMANENT,
            source=ContactDetailSource.CLIENT,
            status="verified"
        )
        
        customer = Customer(
            first_name="John",
            last_name="Doe",
            contact_details=[contact]
        )
        
        api_body = customer.to_api_body()
        
        assert "contact_details" in api_body
        assert len(api_body["contact_details"]) == 1
        
        contact_data = api_body["contact_details"][0]
        assert contact_data["type"] == "email"  # Enum serialized as string
        assert contact_data["value"] == "john@example.com"
        assert contact_data["primary"] is True
        assert contact_data["usage"] == "permanent"
        assert contact_data["source"] == "client"
        assert contact_data["status"] == "verified"

    def test_customer_date_serialization_in_api_body(self):
        """Test that date fields are properly serialized in to_api_body."""
        customer = Customer(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 15)
        )
        
        api_body = customer.to_api_body()
        
        # Date should be serialized as ISO format string
        assert api_body["date_of_birth"] == "1990-01-15"
        assert isinstance(api_body["date_of_birth"], str)

    def test_customer_mixed_contact_detail_types(self):
        """Test customer with mixed contact detail types (enum and string)."""
        # This tests backward compatibility
        contact1 = ContactDetail(
            type=ContactDetailType.EMAIL,  # Using enum
            value="john@example.com"
        )
        
        contact2 = ContactDetail(
            type="phone_number",  # Using string
            value="+44123456789"
        )
        
        customer = Customer(
            first_name="John",
            last_name="Doe",
            contact_details=[contact1, contact2]
        )
        
        api_body = customer.to_api_body()
        
        contact_details = api_body["contact_details"]
        assert contact_details[0]["type"] == "email"
        assert contact_details[1]["type"] == "phone_number"
