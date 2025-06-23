"""
Unit tests for Debt model and DebtStatus enum.
"""

import pytest
from datetime import datetime, date

from ophelos_sdk.models import Debt, DebtStatus, Customer, Organisation


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
        assert api_body["start_at"] == date(2024, 1, 1)
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
