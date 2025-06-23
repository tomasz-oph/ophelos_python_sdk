"""
Unit tests for Debt model and DebtStatus enum.
"""

import pytest
from datetime import datetime, date

from ophelos_sdk.models import (
    Debt,
    DebtStatus,
    StatusObject,
    DebtSummary,
    SummaryBreakdown,
    Customer,
    Organisation,
    Currency,
)


class TestDebtModel:
    """Test cases for Debt model."""

    def test_debt_creation(self, sample_debt_data):
        """Test debt model creation with valid data."""
        debt = Debt(**sample_debt_data)

        assert debt.id == sample_debt_data["id"]
        assert debt.summary.amount_total == sample_debt_data["summary"]["amount_total"]
        assert debt.status.value == DebtStatus.PREPARED
        assert debt.currency == "GBP"
        assert debt.customer == sample_debt_data["customer"]
        assert debt.organisation == sample_debt_data["organisation"]
        assert debt.metadata == sample_debt_data["metadata"]

    def test_debt_status_enum(self):
        """Test debt status enumeration."""
        assert DebtStatus.PREPARED == "prepared"
        assert DebtStatus.ANALYSING == "analysing"
        assert DebtStatus.CLOSED == "closed"
        assert DebtStatus.WITHDRAWN == "withdrawn"

    def test_debt_optional_fields(self):
        """Test debt creation with minimal required fields."""
        created_at = datetime.now()
        updated_at = datetime.now()
        minimal_data = {
            "id": "debt_123",
            "object": "debt",
            "status": {
                "value": "prepared",
                "whodunnit": "system",
                "context": None,
                "reason": None,
                "updated_at": updated_at.isoformat(),
            },
            "customer": "cust_123",
            "organisation": "org_123",
            "summary": {"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            "created_at": created_at,
            "updated_at": updated_at,
        }

        debt = Debt(**minimal_data)
        assert debt.id == "debt_123"
        assert debt.account_number is None
        assert debt.reference_code is None
        assert debt.metadata is None

    def test_debt_to_api_body_basic(self):
        """Test debt to_api_body with basic fields."""
        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            customer="cust_123",
            organisation="org_123",
            summary={"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()

        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body
        assert api_body["customer"] == "cust_123"
        assert api_body["organisation"] == "org_123"
        # status and summary are not in __api_body_fields__ for debt
        assert "status" not in api_body
        assert "summary" not in api_body

    def test_debt_to_api_body_with_customer_model(self):
        """Test debt to_api_body with customer model (should convert to ID)."""
        customer_model = Customer(
            id="cust_real_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            customer=customer_model,
            organisation="org_123",
            summary={"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()

        assert api_body["customer"] == "cust_real_123"

    def test_debt_to_api_body_with_temp_customer_model(self):
        """Test debt to_api_body with temp customer model (should include full object)."""
        customer_model = Customer(
            id="temp_cust_123",
            object="customer",
            first_name="John",
            last_name="Doe",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            customer=customer_model,
            organisation="org_123",
            summary={"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()

        assert isinstance(api_body["customer"], dict)
        assert api_body["customer"]["first_name"] == "John"
        assert api_body["customer"]["last_name"] == "Doe"
        assert "id" not in api_body["customer"]

    def test_debt_to_api_body_with_all_fields(self):
        """Test debt to_api_body with all optional fields."""
        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            kind="credit_card",
            reference_code="REF-001",
            account_number="ACC-001",
            customer="cust_123",
            organisation="org_123",
            currency="GBP",
            summary={"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            tags=["urgent", "vip"],
            configurations={"payment_reminder": True},
            start_at=date(2024, 1, 1),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"source": "api", "priority": "high"},
        )

        api_body = debt.to_api_body()

        assert api_body["kind"] == "credit_card"
        assert api_body["reference_code"] == "REF-001"
        assert api_body["account_number"] == "ACC-001"
        assert api_body["currency"] == "GBP"
        assert api_body["tags"] == ["urgent", "vip"]
        assert api_body["configurations"] == {"payment_reminder": True}
        assert api_body["start_at"] == "2024-01-01"  # Date is serialized as ISO string
        assert api_body["metadata"] == {"source": "api", "priority": "high"}

    def test_debt_api_body_fields_configuration(self):
        """Test that debt uses correct __api_body_fields__ configuration."""
        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            customer="cust_123",
            organisation="org_123",
            summary={"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()
        expected_fields = {
            "kind",
            "reference_code",
            "account_number",
            "customer",
            "customer_id",
            "organisation",
            "organisation_id",
            "originator",
            "currency",
            "invoices",
            "line_items",
            "payments",
            "tags",
            "configurations",
            "start_at",
            "metadata",
        }

        # Only non-None fields should be included (due to exclude_none=True default)
        for field in api_body.keys():
            assert field in expected_fields or field in ["status", "summary"]

    def test_debt_balance_amount_property(self):
        """Test debt balance_amount computed property."""
        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            customer="cust_123",
            organisation="org_123",
            summary={"amount_total": 10000, "amount_paid": 3000, "amount_remaining": 7000},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert debt.balance_amount == 7000

    def test_debt_to_api_body_server_field_exclusion(self):
        """Test that debt excludes all server fields from API body."""
        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            customer="cust_123",
            organisation="org_123",
            summary={"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()

        server_fields = {"id", "object", "created_at", "updated_at"}
        for field in server_fields:
            assert field not in api_body


class TestUpdatedDebtStatus:
    """Test cases for updated DebtStatus enum."""

    def test_new_debt_statuses(self):
        """Test new debt status enumeration values."""
        # Test new statuses
        assert DebtStatus.DELETED == "deleted"
        assert DebtStatus.CONTACT_FAILED == "contact_failed"
        assert DebtStatus.ENRICHING == "enriching"
        assert DebtStatus.DISCHARGED == "discharged"
        assert DebtStatus.OPEN == "open"

    def test_british_spelling(self):
        """Test British spelling for analysing."""
        assert DebtStatus.ANALYSING == "analysing"

    def test_status_categories(self):
        """Test debt statuses are properly categorized."""
        # Client flow
        assert DebtStatus.INITIALIZING == "initializing"
        assert DebtStatus.PREPARED == "prepared"
        assert DebtStatus.PAUSED == "paused"
        assert DebtStatus.WITHDRAWN == "withdrawn"
        assert DebtStatus.DELETED == "deleted"

        # Customer Operations
        assert DebtStatus.ASSESSING == "assessing"
        assert DebtStatus.RECOVERING == "recovering"
        assert DebtStatus.PROCESS_EXHAUSTED == "process_exhausted"

        # Legal flow
        assert DebtStatus.LEGAL_PROTECTION == "legal_protection"


class TestDebtStatusEnum:
    """Test cases for DebtStatus enum."""

    def test_debt_status_enum_completeness(self):
        """Test that all debt status enum values are defined."""
        expected_statuses = {
            # Client flow
            "initializing",
            "prepared",
            "paused",
            "withdrawn",
            "deleted",
            # Ophelos Flow
            "analysing",
            "resumed",
            "contacted",
            "contact_established",
            "contact_failed",
            "enriching",
            "returned",
            "discharged",
            # Customer Flow
            "arranging",
            "paying",
            "settled",
            "paid",
            # Action Required
            "queried",
            "disputed",
            "defaulted",
            "follow_up_required",
            "adjusted",
            # Customer Operations
            "assessing",
            "recovering",
            "process_exhausted",
            # Legal flow
            "legal_protection",
            # Legacy
            "closed",
            "open",
        }

        actual_statuses = {member.value for member in DebtStatus}
        assert actual_statuses == expected_statuses

    def test_debt_status_specific_values(self):
        """Test specific debt status enum values."""
        # Client flow
        assert DebtStatus.INITIALIZING == "initializing"
        assert DebtStatus.PREPARED == "prepared"
        assert DebtStatus.PAUSED == "paused"
        assert DebtStatus.WITHDRAWN == "withdrawn"
        assert DebtStatus.DELETED == "deleted"

        # Ophelos Flow
        assert DebtStatus.ANALYSING == "analysing"
        assert DebtStatus.RESUMED == "resumed"
        assert DebtStatus.CONTACTED == "contacted"
        assert DebtStatus.CONTACT_ESTABLISHED == "contact_established"
        assert DebtStatus.CONTACT_FAILED == "contact_failed"
        assert DebtStatus.ENRICHING == "enriching"
        assert DebtStatus.RETURNED == "returned"
        assert DebtStatus.DISCHARGED == "discharged"

        # Customer Flow
        assert DebtStatus.ARRANGING == "arranging"
        assert DebtStatus.PAYING == "paying"
        assert DebtStatus.SETTLED == "settled"
        assert DebtStatus.PAID == "paid"

        # Action Required
        assert DebtStatus.QUERIED == "queried"
        assert DebtStatus.DISPUTED == "disputed"
        assert DebtStatus.DEFAULTED == "defaulted"
        assert DebtStatus.FOLLOW_UP_REQUIRED == "follow_up_required"
        assert DebtStatus.ADJUSTED == "adjusted"

        # Customer Operations
        assert DebtStatus.ASSESSING == "assessing"
        assert DebtStatus.RECOVERING == "recovering"
        assert DebtStatus.PROCESS_EXHAUSTED == "process_exhausted"

        # Legal flow
        assert DebtStatus.LEGAL_PROTECTION == "legal_protection"

        # Legacy
        assert DebtStatus.CLOSED == "closed"
        assert DebtStatus.OPEN == "open"


class TestStatusObject:
    """Test cases for StatusObject model."""

    def test_status_object_creation_with_enum(self):
        """Test status object creation with enum value."""
        status = StatusObject(
            value=DebtStatus.PREPARED,
            whodunnit="system",
            context="automated",
            reason="initial_setup",
            updated_at=datetime.now(),
        )

        assert status.value == DebtStatus.PREPARED
        assert status.whodunnit == "system"
        assert status.context == "automated"
        assert status.reason == "initial_setup"
        assert isinstance(status.updated_at, datetime)

    def test_status_object_creation_with_string(self):
        """Test status object creation with string value."""
        status = StatusObject(value="paying", whodunnit="customer", updated_at=datetime.now())

        assert status.value == "paying"
        assert status.whodunnit == "customer"
        assert status.context is None
        assert status.reason is None

    def test_status_object_minimal_creation(self):
        """Test status object creation with minimal fields."""
        status = StatusObject(value=DebtStatus.ANALYSING, updated_at=datetime.now())

        assert status.value == DebtStatus.ANALYSING
        assert status.whodunnit is None
        assert status.context is None
        assert status.reason is None


class TestDebtSummaryModels:
    """Test cases for DebtSummary and SummaryBreakdown models."""

    def test_summary_breakdown_creation(self):
        """Test summary breakdown creation."""
        breakdown = SummaryBreakdown(
            principal=10000,
            interest=500,
            fees=100,
            discounts=-200,
            charges=50,
            value_added_tax=210,
            miscellaneous=25,
            refunds=-100,
        )

        assert breakdown.principal == 10000
        assert breakdown.interest == 500
        assert breakdown.fees == 100
        assert breakdown.discounts == -200
        assert breakdown.charges == 50
        assert breakdown.value_added_tax == 210
        assert breakdown.miscellaneous == 25
        assert breakdown.refunds == -100

    def test_debt_summary_creation(self):
        """Test debt summary creation."""
        breakdown = SummaryBreakdown(principal=10000, interest=500, fees=100)

        summary = DebtSummary(
            amount_total=10600,
            amount_paid=2000,
            amount_remaining=8600,
            breakdown=breakdown,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert summary.amount_total == 10600
        assert summary.amount_paid == 2000
        assert summary.amount_remaining == 8600
        assert isinstance(summary.breakdown, SummaryBreakdown)
        assert summary.breakdown.principal == 10000


class TestDebtModelEnhanced:
    """Enhanced test cases for Debt model."""

    def test_debt_creation_with_status_object(self):
        """Test debt creation with StatusObject."""
        status = StatusObject(value=DebtStatus.PREPARED, whodunnit="system", updated_at=datetime.now())

        summary = DebtSummary(amount_total=10000, amount_paid=0, amount_remaining=10000)

        debt = Debt(
            id="debt_123",
            object="debt",
            status=status,
            kind="credit_card",
            customer="cust_123",
            organisation="org_123",
            currency=Currency.GBP,
            summary=summary,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert debt.id == "debt_123"
        assert isinstance(debt.status, StatusObject)
        assert debt.status.value == DebtStatus.PREPARED
        assert debt.currency == Currency.GBP
        assert isinstance(debt.summary, DebtSummary)

    def test_debt_to_api_body_with_currency_enum(self):
        """Test debt to_api_body with Currency enum."""
        debt = Debt(
            id="debt_123",
            kind="personal_loan",
            customer="cust_123",
            organisation="org_123",
            currency=Currency.EUR,
            reference_code="REF-2024-001",
            account_number="ACC-123456",
            tags=["priority", "vip"],
            metadata={"source": "api", "channel": "web"},
        )

        api_body = debt.to_api_body()

        assert api_body["kind"] == "personal_loan"
        assert api_body["currency"] == "EUR"  # Enum serialized as string
        assert api_body["reference_code"] == "REF-2024-001"
        assert api_body["account_number"] == "ACC-123456"
        assert api_body["customer"] == "cust_123"
        assert api_body["organisation"] == "org_123"
        assert api_body["tags"] == ["priority", "vip"]
        assert api_body["metadata"] == {"source": "api", "channel": "web"}

    def test_debt_to_api_body_with_nested_models(self):
        """Test debt to_api_body with nested customer and organisation models."""
        customer = Customer(id="cust_real_456", first_name="Jane", last_name="Smith")

        organisation = Organisation(
            id="org_real_789", name="Test Organisation", created_at=datetime.now(), updated_at=datetime.now()
        )

        debt = Debt(id="debt_456", customer=customer, organisation=organisation, kind="mortgage", currency=Currency.USD)

        api_body = debt.to_api_body()

        # Real IDs should be converted to ID references
        assert api_body["customer"] == "cust_real_456"
        assert api_body["organisation"] == "org_real_789"
        assert api_body["kind"] == "mortgage"
        assert api_body["currency"] == "USD"

    def test_debt_to_api_body_with_temp_models(self):
        """Test debt to_api_body with temporary customer/organisation models."""
        temp_customer = Customer(id="temp_cust_123", first_name="Temp", last_name="Customer")

        debt = Debt(id="debt_789", customer=temp_customer, organisation="org_123", kind="credit_card")

        api_body = debt.to_api_body()

        # Temp customer should be included as full object
        assert isinstance(api_body["customer"], dict)
        assert api_body["customer"]["first_name"] == "Temp"
        assert api_body["customer"]["last_name"] == "Customer"
        # Organisation ID should remain as string
        assert api_body["organisation"] == "org_123"

    def test_debt_balance_amount_property_with_summary(self):
        """Test debt balance_amount property with DebtSummary."""
        summary = DebtSummary(amount_total=15000, amount_paid=5000, amount_remaining=10000)

        debt = Debt(id="debt_balance_test", summary=summary)

        assert debt.balance_amount == 10000

    def test_debt_balance_amount_property_without_summary(self):
        """Test debt balance_amount property without summary."""
        debt = Debt(id="debt_no_summary")

        assert debt.balance_amount == 0

    def test_debt_date_serialization_in_api_body(self):
        """Test that date fields are properly serialized in to_api_body."""
        debt = Debt(
            id="debt_date_test", customer="cust_123", organisation="org_123", start_at=date(2024, 3, 15), kind="loan"
        )

        api_body = debt.to_api_body()

        # Date should be serialized as ISO format string
        assert api_body["start_at"] == "2024-03-15"
        assert isinstance(api_body["start_at"], str)

    def test_debt_api_body_excludes_server_fields(self):
        """Test that debt API body excludes server-generated fields."""
        debt = Debt(
            id="debt_server_test",
            object="debt",
            status=StatusObject(value=DebtStatus.PREPARED, updated_at=datetime.now()),
            summary=DebtSummary(amount_total=10000),
            customer="cust_123",
            organisation="org_123",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()

        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "status" not in api_body
        assert "summary" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # Client fields should be included
        assert api_body["customer"] == "cust_123"
        assert api_body["organisation"] == "org_123"
