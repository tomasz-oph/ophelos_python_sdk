"""
Unit tests for Debt model and DebtStatus enum.
"""

import pytest
from datetime import datetime

from ophelos.models import Debt, DebtStatus


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