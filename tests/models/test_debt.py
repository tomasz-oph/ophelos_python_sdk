"""
Unit tests for Debt model and DebtStatus enum.
"""

from datetime import date, datetime

from ophelos_sdk.models import (
    Currency,
    Customer,
    Debt,
    DebtStatus,
    DebtSummary,
    Organisation,
    StatusObject,
    SummaryBreakdown,
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
        # String IDs should be converted to _id fields
        assert "customer" not in api_body
        assert "organisation" not in api_body
        assert api_body["customer_id"] == "cust_123"
        assert api_body["organisation_id"] == "org_123"
        # status and summary are not in __api_body_fields__ for debt
        assert "status" not in api_body
        assert "summary" not in api_body

    def test_debt_to_api_body_with_customer_model(self):
        """Test debt to_api_body with customer model (should convert to customer_id)."""
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

        # Should convert customer model to customer_id
        assert "customer" not in api_body
        assert api_body["customer_id"] == "cust_real_123"
        assert "organisation" not in api_body
        assert api_body["organisation_id"] == "org_123"

    def test_debt_to_api_body_with_organisation_model(self):
        """Test debt to_api_body with organisation model (should convert to organisation_id)."""
        organisation_model = Organisation(
            id="org_real_456",
            object="organisation",
            name="ACME Corp",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        debt = Debt(
            id="debt_123",
            object="debt",
            customer="cust_123",
            organisation=organisation_model,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        api_body = debt.to_api_body()

        # Should convert organisation model to organisation_id
        assert "organisation" not in api_body
        assert api_body["organisation_id"] == "org_real_456"

    def test_debt_to_api_body_with_both_models(self):
        """Test debt to_api_body with both customer and organisation models."""
        customer_model = Customer(
            id="cust_real_123",
            object="customer",
            first_name="John",
            last_name="Doe",
        )

        organisation_model = Organisation(
            id="org_real_456",
            object="organisation",
            name="ACME Corp",
        )

        debt = Debt(
            id="debt_123",
            customer=customer_model,
            organisation=organisation_model,
        )

        api_body = debt.to_api_body()

        # Should convert both models to their respective ID fields
        assert "customer" not in api_body
        assert "organisation" not in api_body
        assert api_body["customer_id"] == "cust_real_123"
        assert api_body["organisation_id"] == "org_real_456"

    def test_debt_to_api_body_with_string_ids(self):
        """Test debt to_api_body with string customer/organisation IDs."""
        debt = Debt(
            id="debt_123",
            customer="cust_string_123",
            organisation="org_string_456",
        )

        api_body = debt.to_api_body()

        # Should convert string IDs to _id fields
        assert "customer" not in api_body
        assert "organisation" not in api_body
        assert api_body["customer_id"] == "cust_string_123"
        assert api_body["organisation_id"] == "org_string_456"

    def test_debt_to_api_body_with_temp_customer_model(self):
        """Test debt to_api_body with temp customer model (should not convert to ID)."""
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

        # Should not convert temp ID to customer_id
        assert "customer_id" not in api_body
        assert isinstance(api_body["customer"], dict)
        assert api_body["customer"]["first_name"] == "John"
        assert api_body["customer"]["last_name"] == "Doe"
        assert "id" not in api_body["customer"]  # Server fields excluded
        # Should convert organisation string ID to organisation_id
        assert "organisation" not in api_body
        assert api_body["organisation_id"] == "org_123"

    def test_debt_to_api_body_with_temp_organisation_model(self):
        """Test debt to_api_body with temp organisation model (should not convert to ID)."""
        organisation_model = Organisation(
            id="temp_org_456",
            object="organisation",
            name="ACME Corp",
        )

        debt = Debt(
            id="debt_123",
            customer="cust_123",
            organisation=organisation_model,
        )

        api_body = debt.to_api_body()

        # Should not convert temp ID to organisation_id
        assert "organisation_id" not in api_body
        assert isinstance(api_body["organisation"], dict)
        assert api_body["organisation"]["name"] == "ACME Corp"
        assert "id" not in api_body["organisation"]  # Server fields excluded
        # Should convert customer string ID to customer_id
        assert "customer" not in api_body
        assert api_body["customer_id"] == "cust_123"

    def test_debt_to_api_body_with_customer_model_without_id(self):
        """Test debt to_api_body with customer model without ID."""
        customer_model = Customer(
            object="customer",
            first_name="John",
            last_name="Doe",
        )

        debt = Debt(
            id="debt_123",
            customer=customer_model,
            organisation="org_123",
        )

        api_body = debt.to_api_body()

        # Should not convert to customer_id since no ID
        assert "customer_id" not in api_body
        assert isinstance(api_body["customer"], dict)
        assert api_body["customer"]["first_name"] == "John"
        # Should convert organisation string ID to organisation_id
        assert "organisation" not in api_body
        assert api_body["organisation_id"] == "org_123"

    def test_debt_to_api_body_mixed_scenarios(self):
        """Test debt to_api_body with mixed customer/organisation scenarios."""
        customer_model = Customer(id="cust_real_123", first_name="John")

        debt = Debt(
            id="debt_123",
            customer=customer_model,  # Model with ID -> should convert
            organisation="org_string_456",  # String ID -> should convert
        )

        api_body = debt.to_api_body()

        assert "customer" not in api_body
        assert "organisation" not in api_body
        assert api_body["customer_id"] == "cust_real_123"
        assert api_body["organisation_id"] == "org_string_456"

    def test_debt_to_api_body_with_all_fields(self):
        """Test debt to_api_body with all optional fields."""
        debt = Debt(
            id="debt_123",
            object="debt",
            status={"value": "prepared", "whodunnit": "system", "updated_at": datetime.now()},
            kind="credit_card",
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
        assert api_body["account_number"] == "ACC-001"
        assert api_body["currency"] == "GBP"
        assert api_body["tags"] == ["urgent", "vip"]
        assert api_body["configurations"] == {"payment_reminder": True}
        assert api_body["start_at"] == "2024-01-01"  # Date is serialized as ISO string
        assert api_body["metadata"] == {"source": "api", "priority": "high"}
        # Verify customer/organisation string IDs are converted to _id fields
        assert "customer" not in api_body
        assert "organisation" not in api_body
        assert api_body["customer_id"] == "cust_123"
        assert api_body["organisation_id"] == "org_123"

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
            account_number="ACC-123456",
            tags=["priority", "vip"],
            metadata={"source": "api", "channel": "web"},
        )

        api_body = debt.to_api_body()

        assert api_body["kind"] == "personal_loan"
        assert api_body["currency"] == "EUR"  # Enum serialized as string
        assert api_body["account_number"] == "ACC-123456"
        # String IDs converted to _id fields
        assert api_body["customer_id"] == "cust_123"
        assert api_body["organisation_id"] == "org_123"
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
        assert api_body["customer_id"] == "cust_real_456"
        assert api_body["organisation_id"] == "org_real_789"
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
        # Organisation string ID should be converted to organisation_id
        assert api_body["organisation_id"] == "org_123"

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
            id="debt_date_test",
            kind="personal_loan",
            customer="cust_456",
            organisation="org_456",
            currency=Currency.GBP,
            start_at=date(2024, 2, 1),
            metadata={"created_by": "api", "test_date": True},
        )

        api_body = debt.to_api_body()

        # Date should be serialized as ISO format string
        assert api_body["start_at"] == "2024-02-01"
        assert isinstance(api_body["start_at"], str)
