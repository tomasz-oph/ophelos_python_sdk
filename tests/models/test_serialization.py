"""
Unit tests for model serialization and deserialization.
"""

import pytest
from datetime import datetime

from ophelos_sdk.models import Debt


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_debt_json_serialization(self, sample_debt_data):
        """Test debt model JSON serialization."""
        debt = Debt(**sample_debt_data)

        # Convert to dict (similar to JSON serialization)
        debt_dict = debt.model_dump()

        assert debt_dict["id"] == sample_debt_data["id"]
        assert debt_dict["summary"]["amount_total"] == sample_debt_data["summary"]["amount_total"]
        assert debt_dict["status"]["value"] == sample_debt_data["status"]["value"]

    def test_model_extra_fields(self):
        """Test that models accept extra fields (for API compatibility)."""
        created_at = datetime.now()
        updated_at = datetime.now()
        debt_data = {
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
            "unknown_field": "should_be_accepted",  # Extra field
        }

        # Should not raise an error due to extra="allow" in BaseOphelosModel
        debt = Debt(**debt_data)
        assert debt.id == "debt_123"
        # Extra field should be accessible
        assert hasattr(debt, "unknown_field")
        assert debt.unknown_field == "should_be_accepted"
