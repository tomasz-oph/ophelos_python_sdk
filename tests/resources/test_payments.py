"""
Unit tests for payments resource.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import Currency, PaginatedResponse, Payment
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

    def test_create_payment_with_dict(self, payments_resource, mock_http_client, sample_payment_data):
        """Test creating a payment with dictionary data."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_payment_data, mock_response)

        payment_data = {
            "transaction_at": "2023-12-01T10:30:00",
            "transaction_ref": "CREATE-REF-001",
            "amount": 10000,
            "currency": "GBP",
            "metadata": {"source": "test_create"},
        }

        result = payments_resource.create("debt_123", payment_data)

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/payments", data=payment_data, return_response=True
        )
        assert isinstance(result, Payment)
        assert result.id == sample_payment_data["id"]

    def test_create_payment_with_model(self, payments_resource, mock_http_client, sample_payment_data):
        """Test creating a payment with Payment model instance."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_payment_data, mock_response)

        payment_model = Payment(
            transaction_at=datetime(2023, 12, 1, 10, 30, 0),
            transaction_ref="CREATE-MODEL-001",
            amount=15000,
            currency=Currency.GBP,
            metadata={"source": "test_create_model"},
        )

        result = payments_resource.create("debt_123", payment_model)

        # Verify the model was serialized correctly
        expected_data = {
            "transaction_at": "2023-12-01T10:30:00",
            "transaction_ref": "CREATE-MODEL-001",
            "amount": 15000,
            "currency": "GBP",
            "metadata": {"source": "test_create_model"},
        }
        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/payments", data=expected_data, return_response=True
        )
        assert isinstance(result, Payment)

    def test_create_payment_with_expand(self, payments_resource, mock_http_client, sample_payment_data):
        """Test creating a payment with expand parameter."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_payment_data, mock_response)

        payment_data = {
            "transaction_at": "2023-12-01T10:30:00",
            "transaction_ref": "CREATE-EXPAND-001",
            "amount": 10000,
            "currency": "GBP",
        }

        result = payments_resource.create("debt_123", payment_data, expand=["debt"])

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/payments", data=payment_data, params={"expand[]": ["debt"]}, return_response=True
        )
        assert isinstance(result, Payment)

    def test_update_payment_with_dict(self, payments_resource, mock_http_client, sample_payment_data):
        """Test updating a payment with dictionary data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        update_data = {
            "transaction_ref": "UPDATED-REF-001",
            "metadata": {"status": "verified", "updated_at": "2023-12-01T16:00:00"},
        }

        result = payments_resource.update("debt_123", "pay_456", update_data)

        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=update_data, return_response=True
        )
        assert isinstance(result, Payment)
        assert result.id == sample_payment_data["id"]

    def test_update_payment_with_model(self, payments_resource, mock_http_client, sample_payment_data):
        """Test updating a payment with Payment model instance."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        payment_model = Payment(
            transaction_ref="UPDATED-MODEL-001", amount=30000, metadata={"source": "test_update_model"}
        )

        result = payments_resource.update("debt_123", "pay_456", payment_model)

        # Verify the model was serialized correctly
        expected_data = {
            "transaction_ref": "UPDATED-MODEL-001",
            "amount": 30000,
            "metadata": {"source": "test_update_model"},
        }
        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=expected_data, return_response=True
        )
        assert isinstance(result, Payment)

    def test_update_payment_with_expand(self, payments_resource, mock_http_client, sample_payment_data):
        """Test updating a payment with expand parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        update_data = {"transaction_ref": "UPDATED-EXPAND-001"}

        result = payments_resource.update("debt_123", "pay_456", update_data, expand=["debt"])

        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=update_data, params={"expand[]": ["debt"]}, return_response=True
        )
        assert isinstance(result, Payment)

    def test_update_payment_partial_metadata_only(self, payments_resource, mock_http_client, sample_payment_data):
        """Test updating a payment with only metadata (partial update)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        # Create Payment model with only metadata
        payment_model = Payment(metadata={"status": "verified", "notes": "Customer confirmed"})

        result = payments_resource.update("debt_123", "pay_456", payment_model)

        # Verify only metadata was sent
        expected_data = {"metadata": {"status": "verified", "notes": "Customer confirmed"}}
        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=expected_data, return_response=True
        )
        assert isinstance(result, Payment)

    def test_update_payment_partial_transaction_ref_only(
        self, payments_resource, mock_http_client, sample_payment_data
    ):
        """Test updating a payment with only transaction_ref (partial update)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        # Create Payment model with only transaction_ref
        payment_model = Payment(transaction_ref="CORRECTED-REF-789")

        result = payments_resource.update("debt_123", "pay_456", payment_model)

        # Verify only transaction_ref was sent
        expected_data = {"transaction_ref": "CORRECTED-REF-789"}
        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=expected_data, return_response=True
        )
        assert isinstance(result, Payment)

    def test_create_payment_model_serialization(self, payments_resource, mock_http_client, sample_payment_data):
        """Test that Payment model instances are properly serialized when creating."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_payment_data, mock_response)

        # Create Payment model with datetime that needs serialization
        payment_model = Payment(
            transaction_at=datetime(2023, 12, 1, 14, 30, 45),
            transaction_ref="SERIALIZE-TEST-001",
            amount=25000,
            currency=Currency.EUR,
            metadata={"processor": "test", "fee": 500},
        )

        payments_resource.create("debt_123", payment_model)

        # Verify datetime was serialized to ISO format
        expected_data = {
            "transaction_at": "2023-12-01T14:30:45",
            "transaction_ref": "SERIALIZE-TEST-001",
            "amount": 25000,
            "currency": "EUR",
            "metadata": {"processor": "test", "fee": 500},
        }
        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/payments", data=expected_data, return_response=True
        )

    def test_update_payment_model_serialization(self, payments_resource, mock_http_client, sample_payment_data):
        """Test that Payment model instances are properly serialized when updating."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        # Create Payment model with datetime that needs serialization
        payment_model = Payment(
            transaction_at=datetime(2023, 12, 1, 16, 45, 30),
            currency=Currency.USD,
            metadata={"updated": True, "timestamp": "2023-12-01T16:45:30"},
        )

        payments_resource.update("debt_123", "pay_456", payment_model)

        # Verify datetime was serialized to ISO format
        expected_data = {
            "transaction_at": "2023-12-01T16:45:30",
            "currency": "USD",
            "metadata": {"updated": True, "timestamp": "2023-12-01T16:45:30"},
        }
        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=expected_data, return_response=True
        )

    def test_create_payment_without_expand(self, payments_resource, mock_http_client, sample_payment_data):
        """Test creating a payment without expand parameter (default behavior)."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_payment_data, mock_response)

        payment_data = {
            "transaction_at": "2023-12-01T10:30:00",
            "transaction_ref": "NO-EXPAND-001",
            "amount": 10000,
            "currency": "GBP",
        }

        payments_resource.create("debt_123", payment_data)

        # Verify no params were sent when expand is not provided
        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/payments", data=payment_data, return_response=True
        )

    def test_update_payment_without_expand(self, payments_resource, mock_http_client, sample_payment_data):
        """Test updating a payment without expand parameter (default behavior)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_payment_data, mock_response)

        update_data = {"transaction_ref": "NO-EXPAND-UPDATE-001"}

        payments_resource.update("debt_123", "pay_456", update_data)

        # Verify no params were sent when expand is not provided
        mock_http_client.put.assert_called_once_with(
            "debts/debt_123/payments/pay_456", data=update_data, return_response=True
        )
