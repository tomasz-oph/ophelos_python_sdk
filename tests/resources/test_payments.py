"""
Unit tests for payments resource.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import PaginatedResponse, Payment
from ophelos_sdk.resources import PaymentsResource


class TestPaymentsResource:
    """Test cases for payments resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def payments_resource(self, mock_http_client):
        """Create payments resource for testing."""
        return PaymentsResource(mock_http_client)

    def test_list_payments(self, payments_resource, mock_http_client, sample_payment_data, sample_paginated_response):
        """Test listing payments."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_payment_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = payments_resource.list(limit=20)

        mock_http_client.get.assert_called_once_with("payments", params={"limit": 20}, return_response=True)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Payment)

    def test_search_payments(self, payments_resource, mock_http_client, sample_payment_data, sample_paginated_response):
        """Test searching payments."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_payment_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = payments_resource.search("status:succeeded")

        mock_http_client.get.assert_called_once_with(
            "payments/search", params={"query": "status:succeeded"}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Payment)

    def test_get_payment(self, payments_resource, mock_http_client, sample_payment_data):
        """Test getting a specific payment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_payment_data, mock_response)

        result = payments_resource.get("pay_123")

        mock_http_client.get.assert_called_once_with("payments/pay_123", params={}, return_response=True)
        assert isinstance(result, Payment)
        assert result.id == sample_payment_data["id"]
