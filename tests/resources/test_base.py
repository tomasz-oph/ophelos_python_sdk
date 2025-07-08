"""
Unit tests for base resource functionality.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.resources import DebtsResource


class TestBaseResource:
    """Test cases for base resource functionality."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def debts_resource(self, mock_http_client):
        """Create debts resource for testing."""
        return DebtsResource(mock_http_client)

    def test_build_expand_params(self, debts_resource):
        """Test building expand parameters."""
        # No expand fields
        params = debts_resource._build_expand_params()
        assert params == {}

        # Single expand field
        params = debts_resource._build_expand_params(["customer"])
        assert params == {"expand[]": ["customer"]}

        # Multiple expand fields
        params = debts_resource._build_expand_params(["customer", "payments"])
        assert params == {"expand[]": ["customer", "payments"]}

    def test_build_list_params(self, debts_resource):
        """Test building list parameters."""
        params = debts_resource._build_list_params(
            limit=10, after="debt_123", before="debt_456", expand=["customer"], extra_param="value"
        )

        expected = {
            "limit": 10,
            "after": "debt_123",
            "before": "debt_456",
            "expand[]": ["customer"],
            "extra_param": "value",
        }
        assert params == expected

    def test_build_search_params(self, debts_resource):
        """Test building search parameters."""
        params = debts_resource._build_search_params(
            query="status:paying", limit=5, expand=["customer"], org_id="org_123"
        )

        expected = {
            "query": "status:paying",
            "limit": 5,
            "expand[]": ["customer"],
            "org_id": "org_123",
        }
        assert params == expected
