"""
Unit tests for debts resource.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import Debt, PaginatedResponse, Payment
from ophelos_sdk.resources import DebtsResource


class TestDebtsResource:
    """Test cases for debts resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def debts_resource(self, mock_http_client):
        """Create debts resource for testing."""
        return DebtsResource(mock_http_client)

    def test_list_debts(self, debts_resource, mock_http_client, sample_debt_data, sample_paginated_response):
        """Test listing debts."""
        # Mock response - keep data as raw dicts, not parsed objects
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_debt_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = debts_resource.list(limit=10, expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "debts", params={"limit": 10, "expand[]": ["customer"]}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        # First item should be parsed as Debt
        assert isinstance(result.data[0], Debt)

    def test_search_debts(self, debts_resource, mock_http_client, sample_debt_data, sample_paginated_response):
        """Test searching debts."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_debt_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = debts_resource.search("status:paying", limit=5)

        mock_http_client.get.assert_called_once_with(
            "debts/search", params={"query": "status:paying", "limit": 5}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Debt)

    def test_get_debt(self, debts_resource, mock_http_client, sample_debt_data):
        """Test getting a specific debt."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_debt_data, mock_response)

        result = debts_resource.get("debt_123", expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "debts/debt_123", params={"expand[]": ["customer"]}, return_response=True
        )
        assert isinstance(result, Debt)
        assert result.id == sample_debt_data["id"]

    def test_create_debt(self, debts_resource, mock_http_client, sample_debt_data):
        """Test creating a debt."""
        create_data = {
            "customer_id": "cust_123",
            "organisation_id": "org_123",
            "total_amount": 10000,
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_debt_data, mock_response)

        result = debts_resource.create(create_data)

        mock_http_client.post.assert_called_once_with("debts", data=create_data, return_response=True)
        assert isinstance(result, Debt)

    def test_update_debt(self, debts_resource, mock_http_client, sample_debt_data):
        """Test updating a debt."""
        update_data = {"metadata": {"updated": True}}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_debt_data, mock_response)

        result = debts_resource.update("debt_123", update_data)

        mock_http_client.put.assert_called_once_with("debts/debt_123", data=update_data, return_response=True)
        assert isinstance(result, Debt)

    def test_delete_debt(self, debts_resource, mock_http_client):
        """Test deleting a debt."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.delete.return_value = ({"deleted": True}, mock_response)

        result = debts_resource.delete("debt_123")

        mock_http_client.delete.assert_called_once_with("debts/debt_123", return_response=True)
        assert result == {"deleted": True}

    def test_debt_lifecycle_operations(self, debts_resource, mock_http_client, sample_debt_data):
        """Test debt lifecycle operations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.post.return_value = (sample_debt_data, mock_response)

        # Test ready operation
        result = debts_resource.ready("debt_123")
        mock_http_client.post.assert_called_with("debts/debt_123/ready", data={}, return_response=True)
        assert isinstance(result, Debt)

        # Test pause operation
        pause_data = {"reason": "customer request"}
        result = debts_resource.pause("debt_123", pause_data)
        mock_http_client.post.assert_called_with("debts/debt_123/pause", data=pause_data, return_response=True)

        # Test resume operation
        result = debts_resource.resume("debt_123")
        mock_http_client.post.assert_called_with("debts/debt_123/resume", data={}, return_response=True)

        # Test withdraw operation
        withdraw_data = {"reason": "fraud"}
        result = debts_resource.withdraw("debt_123", withdraw_data)
        mock_http_client.post.assert_called_with("debts/debt_123/withdraw", data=withdraw_data, return_response=True)

        # Test dispute operation
        dispute_data = {"reason": "amount disputed", "details": "Customer claims incorrect amount"}
        result = debts_resource.dispute("debt_123", dispute_data)
        mock_http_client.post.assert_called_with("debts/debt_123/dispute", data=dispute_data, return_response=True)

    def test_debt_payments_operations(
        self, debts_resource, mock_http_client, sample_payment_data, sample_paginated_response
    ):
        """Test debt payment operations."""
        # Test list payments
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_payment_data]
        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response_obj)

        result = debts_resource.list_payments("debt_123", limit=5)
        mock_http_client.get.assert_called_with("debts/debt_123/payments", params={"limit": 5}, return_response=True)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Payment)

        # Test create payment
        payment_data = {"amount": 5000, "transaction_at": "2024-01-15T10:00:00Z"}
        mock_http_client.post.return_value = (sample_payment_data, mock_response_obj)

        result = debts_resource.create_payment("debt_123", payment_data)
        mock_http_client.post.assert_called_with("debts/debt_123/payments", data=payment_data, return_response=True)
        assert isinstance(result, Payment)

        # Test get payment
        mock_http_client.get.return_value = (sample_payment_data, mock_response_obj)
        result = debts_resource.get_payment("debt_123", "pay_456")
        mock_http_client.get.assert_called_with("debts/debt_123/payments/pay_456", return_response=True)
        assert isinstance(result, Payment)

    def test_get_debt_summary(self, debts_resource, mock_http_client):
        """Test getting debt summary."""
        summary_data = {"total_amount": 10000, "paid_amount": 3000, "remaining": 7000}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (summary_data, mock_response)

        result = debts_resource.get_summary("debt_123")

        mock_http_client.get.assert_called_once_with("debts/debt_123/summary", return_response=True)
        assert result == summary_data
