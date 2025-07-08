"""
Unit tests for line items resource.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import Currency, LineItem, LineItemKind, PaginatedResponse
from ophelos_sdk.resources import LineItemsResource


class TestLineItemsResource:
    """Test cases for line items resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def line_items_resource(self, mock_http_client):
        """Create line items resource for testing."""
        return LineItemsResource(mock_http_client)

    def test_list_line_items(
        self, line_items_resource, mock_http_client, sample_line_item_data, sample_paginated_response
    ):
        """Test listing line items for a debt."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_line_item_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = line_items_resource.list("debt_123", limit=10)

        mock_http_client.get.assert_called_once_with(
            "debts/debt_123/line_items", params={"limit": 10}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], LineItem)
        assert result.data[0].id == sample_line_item_data["id"]

    def test_list_line_items_with_pagination(
        self, line_items_resource, mock_http_client, sample_line_item_data, sample_paginated_response
    ):
        """Test listing line items with pagination parameters."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_line_item_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = line_items_resource.list(
            "debt_123", limit=5, after="li_after_123", before="li_before_456", expand=["debt"]
        )

        mock_http_client.get.assert_called_once_with(
            "debts/debt_123/line_items",
            params={"limit": 5, "after": "li_after_123", "before": "li_before_456", "expand[]": ["debt"]},
            return_response=True,
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], LineItem)

    def test_list_line_items_with_expand(
        self, line_items_resource, mock_http_client, sample_line_item_data, sample_paginated_response
    ):
        """Test listing line items with expand parameters."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_line_item_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = line_items_resource.list("debt_123", expand=["debt", "invoice"])

        mock_http_client.get.assert_called_once_with(
            "debts/debt_123/line_items", params={"expand[]": ["debt", "invoice"]}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)

    def test_list_line_items_with_additional_params(
        self, line_items_resource, mock_http_client, sample_line_item_data, sample_paginated_response
    ):
        """Test listing line items with additional query parameters."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_line_item_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = line_items_resource.list("debt_123", limit=20, kind="debt", currency="GBP")

        mock_http_client.get.assert_called_once_with(
            "debts/debt_123/line_items",
            params={"limit": 20, "kind": "debt", "currency": "GBP"},
            return_response=True,
        )
        assert isinstance(result, PaginatedResponse)

    def test_create_line_item(self, line_items_resource, mock_http_client, sample_line_item_data):
        """Test creating a line item."""
        create_data = {
            "kind": "debt",
            "description": "Principal amount",
            "amount": 100000,
            "currency": "GBP",
            "metadata": {"category": "principal"},
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_line_item_data, mock_response)

        result = line_items_resource.create("debt_123", create_data)

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=create_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.id == sample_line_item_data["id"]
        assert result.kind == sample_line_item_data["kind"]
        assert result.description == sample_line_item_data["description"]
        assert result.amount == sample_line_item_data["amount"]

    def test_create_line_item_with_interest(self, line_items_resource, mock_http_client):
        """Test creating an interest line item."""
        create_data = {
            "kind": "interest",
            "description": "Monthly interest charge",
            "amount": 2500,
            "currency": "GBP",
            "metadata": {"interest_rate": "5.5%"},
        }

        interest_line_item_data = {
            "id": "li_interest_123",
            "object": "line_item",
            "debt_id": "debt_123",
            "kind": "interest",
            "description": "Monthly interest charge",
            "amount": 2500,
            "currency": "GBP",
            "metadata": {"interest_rate": "5.5%"},
        }

        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (interest_line_item_data, mock_response)

        result = line_items_resource.create("debt_123", create_data)

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=create_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.kind == "interest"
        assert result.amount == 2500

    def test_create_line_item_with_negative_amount(self, line_items_resource, mock_http_client):
        """Test creating a credit line item with negative amount."""
        create_data = {
            "kind": "credit",
            "description": "Account credit applied",
            "amount": -5000,
            "currency": "GBP",
            "metadata": {"credit_reason": "overpayment"},
        }

        credit_line_item_data = {
            "id": "li_credit_123",
            "object": "line_item",
            "debt_id": "debt_123",
            "kind": "credit",
            "description": "Account credit applied",
            "amount": -5000,
            "currency": "GBP",
            "metadata": {"credit_reason": "overpayment"},
        }

        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (credit_line_item_data, mock_response)

        result = line_items_resource.create("debt_123", create_data)

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=create_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.kind == "credit"
        assert result.amount == -5000

    def test_create_line_item_with_all_kinds(self, line_items_resource, mock_http_client):
        """Test creating line items with all available kinds."""
        kinds = ["debt", "interest", "fee", "vat", "credit", "discount", "refund", "creditor_refund"]

        for kind in kinds:
            create_data = {
                "kind": kind,
                "description": f"{kind.title()} line item",
                "amount": 1000 if kind not in ["credit", "discount"] else -1000,
                "currency": "GBP",
            }

            line_item_data = {
                "id": f"li_{kind}_123",
                "object": "line_item",
                "debt_id": "debt_123",
                "kind": kind,
                "description": f"{kind.title()} line item",
                "amount": 1000 if kind not in ["credit", "discount"] else -1000,
                "currency": "GBP",
            }

            mock_response = Mock()
            mock_response.status_code = 201
            mock_http_client.post.return_value = (line_item_data, mock_response)

            result = line_items_resource.create("debt_123", create_data)

            assert isinstance(result, LineItem)
            assert result.kind == kind

    def test_create_line_item_with_minimal_data(self, line_items_resource, mock_http_client):
        """Test creating a line item with minimal required data."""
        create_data = {
            "kind": "debt",
            "amount": 50000,
        }

        minimal_line_item_data = {
            "id": "li_minimal_123",
            "object": "line_item",
            "debt_id": "debt_123",
            "kind": "debt",
            "amount": 50000,
        }

        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (minimal_line_item_data, mock_response)

        result = line_items_resource.create("debt_123", create_data)

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=create_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.kind == "debt"
        assert result.amount == 50000

    def test_create_line_item_with_model_instance(self, line_items_resource, mock_http_client, sample_line_item_data):
        """Test creating a line item using a LineItem model instance."""
        # Create a LineItem model instance
        line_item = LineItem(
            kind=LineItemKind.INTEREST,
            description="Test interest charge",
            amount=1500,
            currency=Currency.GBP,
            metadata={"rate": "5.5%"},
        )

        # Create mock response data
        mock_response_data = sample_line_item_data.copy()
        mock_response_data.update(
            {
                "kind": "interest",
                "description": "Test interest charge",
                "amount": 1500,
                "currency": "GBP",
                "metadata": {"rate": "5.5%"},
            }
        )

        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (mock_response_data, mock_response)

        # Pass the LineItem instance directly
        result = line_items_resource.create("debt_123", line_item)

        # Verify the API was called with the serialized data
        expected_data = {
            "kind": "interest",
            "description": "Test interest charge",
            "amount": 1500,
            "currency": "GBP",
            "metadata": {"rate": "5.5%"},
        }
        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=expected_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.kind == "interest"
        assert result.description == "Test interest charge"
        assert result.amount == 1500
        assert result.currency == "GBP"

    def test_create_line_item_with_transaction_at(self, line_items_resource, mock_http_client, sample_line_item_data):
        """Test creating a line item using a LineItem model instance with transaction_at field."""
        from datetime import datetime

        # Create a specific datetime for testing
        transaction_time = datetime(2023, 7, 8, 14, 30, 45)

        # Create a LineItem model instance with transaction_at
        line_item = LineItem(
            kind=LineItemKind.FEE,
            description="Processing fee with timestamp",
            amount=2500,
            currency=Currency.GBP,
            transaction_at=transaction_time,
            metadata={"fee_type": "processing"},
        )

        # Create mock response data
        mock_response_data = sample_line_item_data.copy()
        mock_response_data.update(
            {
                "kind": "fee",
                "description": "Processing fee with timestamp",
                "amount": 2500,
                "currency": "GBP",
                "transaction_at": "2023-07-08T14:30:45",
                "metadata": {"fee_type": "processing"},
            }
        )

        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (mock_response_data, mock_response)

        # Pass the LineItem instance directly
        result = line_items_resource.create("debt_123", line_item)

        # Verify the API was called with the serialized data including transaction_at
        call_args = mock_http_client.post.call_args
        actual_data = call_args[1]["data"]

        assert actual_data["kind"] == "fee"
        assert actual_data["description"] == "Processing fee with timestamp"
        assert actual_data["amount"] == 2500
        assert actual_data["currency"] == "GBP"
        assert actual_data["transaction_at"] == "2023-07-08T14:30:45"  # ISO format
        assert actual_data["metadata"] == {"fee_type": "processing"}

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=actual_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.kind == "fee"
        assert result.description == "Processing fee with timestamp"
        assert result.amount == 2500
        assert result.currency == "GBP"

    def test_create_line_item_with_string_transaction_at(
        self, line_items_resource, mock_http_client, sample_line_item_data
    ):
        """Test creating a line item using a LineItem model instance with string transaction_at."""
        from datetime import datetime

        # Create a LineItem model instance with string transaction_at
        line_item = LineItem(
            kind=LineItemKind.INTEREST,
            description="Interest with string timestamp",
            amount=1200,
            currency=Currency.GBP,
            transaction_at="2023-07-08T14:30:45.123456",  # String input
            metadata={"rate": "4.5%"},
        )

        # Verify the string was automatically converted to datetime
        assert isinstance(line_item.transaction_at, datetime)
        assert line_item.transaction_at == datetime(2023, 7, 8, 14, 30, 45, 123456)

        # Create mock response data
        mock_response_data = sample_line_item_data.copy()
        mock_response_data.update(
            {
                "kind": "interest",
                "description": "Interest with string timestamp",
                "amount": 1200,
                "currency": "GBP",
                "transaction_at": "2023-07-08T14:30:45.123456",
                "metadata": {"rate": "4.5%"},
            }
        )

        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (mock_response_data, mock_response)

        # Pass the LineItem instance directly
        result = line_items_resource.create("debt_123", line_item)

        # Verify the API was called with the serialized data including transaction_at
        call_args = mock_http_client.post.call_args
        actual_data = call_args[1]["data"]

        assert actual_data["kind"] == "interest"
        assert actual_data["description"] == "Interest with string timestamp"
        assert actual_data["amount"] == 1200
        assert actual_data["currency"] == "GBP"
        assert actual_data["transaction_at"] == "2023-07-08T14:30:45.123456"  # ISO format
        assert actual_data["metadata"] == {"rate": "4.5%"}

        mock_http_client.post.assert_called_once_with(
            "debts/debt_123/line_items", data=actual_data, return_response=True
        )
        assert isinstance(result, LineItem)
        assert result.kind == "interest"
        assert result.description == "Interest with string timestamp"
        assert result.amount == 1200
        assert result.currency == "GBP"
