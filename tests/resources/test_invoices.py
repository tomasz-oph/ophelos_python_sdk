"""
Unit tests for InvoicesResource.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

from ophelos_sdk.exceptions import NotFoundError, ValidationError
from ophelos_sdk.models import Currency, Invoice, LineItem, LineItemKind
from ophelos_sdk.resources.invoices import InvoicesResource


class TestInvoicesResource:
    """Test cases for InvoicesResource."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return MagicMock()

    @pytest.fixture
    def invoices_resource(self, mock_http_client):
        """Create an InvoicesResource instance with mock HTTP client."""
        return InvoicesResource(mock_http_client)

    @pytest.fixture
    def sample_invoice_data(self):
        """Sample invoice data for testing."""
        return {
            "id": "inv_123456789",
            "object": "invoice",
            "debt": "debt_987654321",
            "currency": "GBP",
            "reference": "INV-2024-001",
            "status": "outstanding",
            "invoiced_on": "2024-01-15",
            "due_on": "2024-02-15",
            "description": "Test invoice",
            "line_items": ["li_111", "li_222"],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "metadata": {"invoice_type": "standard"},
        }

    @pytest.fixture
    def sample_invoice_model(self):
        """Sample Invoice model for testing."""
        return Invoice(
            reference="INV-MODEL-2024-001",
            description="Test invoice created with model",
            invoiced_on=date(2024, 1, 15),
            due_on=date(2024, 2, 15),
            status="outstanding",
            line_items=[
                LineItem(
                    kind=LineItemKind.DEBT,
                    description="Principal amount",
                    amount=10000,
                    currency=Currency.GBP,
                    transaction_at=datetime.now() - timedelta(hours=1),
                    metadata={"category": "principal"},
                ),
                LineItem(
                    kind=LineItemKind.INTEREST,
                    description="Interest charge",
                    amount=500,
                    currency=Currency.GBP,
                    transaction_at=datetime.now() - timedelta(hours=1),
                    metadata={"rate": "5.0%"},
                ),
            ],
            metadata={"created_by": "test", "department": "billing"},
        )

    def test_get_invoice(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test getting an invoice."""
        debt_id = "debt_123"
        invoice_id = "inv_456"

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.get.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.get(debt_id, invoice_id)

        # Verify HTTP client was called correctly
        mock_http_client.get.assert_called_once_with(
            f"debts/{debt_id}/invoices/{invoice_id}", params={}, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)
        assert result.id == sample_invoice_data["id"]
        assert result.reference == sample_invoice_data["reference"]

    def test_get_invoice_with_expand(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test getting an invoice with expand parameter."""
        debt_id = "debt_123"
        invoice_id = "inv_456"
        expand = ["line_items"]

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.get.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.get(debt_id, invoice_id, expand=expand)

        # Verify HTTP client was called correctly
        mock_http_client.get.assert_called_once_with(
            f"debts/{debt_id}/invoices/{invoice_id}", params={"expand[]": expand}, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)
        assert result.id == sample_invoice_data["id"]

    def test_create_invoice_with_dict(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test creating an invoice with dictionary data."""
        debt_id = "debt_123"
        invoice_data = {
            "reference": "INV-2024-002",
            "description": "Test invoice",
            "status": "outstanding",
            "line_items": [
                {
                    "kind": "debt",
                    "description": "Principal amount",
                    "amount": 10000,
                    "currency": "GBP",
                    "transaction_at": "2024-01-15T09:00:00Z",
                }
            ],
        }

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.post.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.create(debt_id, invoice_data)

        # Verify HTTP client was called correctly
        mock_http_client.post.assert_called_once_with(
            f"debts/{debt_id}/invoices", data=invoice_data, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)
        assert result.id == sample_invoice_data["id"]

    def test_create_invoice_with_model(
        self, invoices_resource, mock_http_client, sample_invoice_data, sample_invoice_model
    ):
        """Test creating an invoice with Invoice model object."""
        debt_id = "debt_123"

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.post.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.create(debt_id, sample_invoice_model)

        # Verify HTTP client was called correctly
        # The model should be converted to API body format
        expected_api_data = sample_invoice_model.to_api_body()
        mock_http_client.post.assert_called_once_with(
            f"debts/{debt_id}/invoices", data=expected_api_data, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)
        assert result.id == sample_invoice_data["id"]

    def test_create_invoice_with_expand(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test creating an invoice with expand parameter."""
        debt_id = "debt_123"
        invoice_data = {"reference": "INV-2024-003", "description": "Test invoice"}
        expand = ["line_items"]

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.post.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.create(debt_id, invoice_data, expand=expand)

        # Verify HTTP client was called correctly
        mock_http_client.post.assert_called_once_with(
            f"debts/{debt_id}/invoices", data=invoice_data, params={"expand[]": expand}, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)

    def test_create_invoice_with_model_and_expand(
        self, invoices_resource, mock_http_client, sample_invoice_data, sample_invoice_model
    ):
        """Test creating an invoice with model object and expand parameter."""
        debt_id = "debt_123"
        expand = ["line_items"]

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.post.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.create(debt_id, sample_invoice_model, expand=expand)

        # Verify HTTP client was called correctly
        expected_api_data = sample_invoice_model.to_api_body()
        mock_http_client.post.assert_called_once_with(
            f"debts/{debt_id}/invoices", data=expected_api_data, params={"expand[]": expand}, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)

    def test_update_invoice_with_dict(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test updating an invoice with dictionary data."""
        debt_id = "debt_123"
        invoice_id = "inv_456"
        update_data = {"description": "Updated test invoice", "status": "paid", "metadata": {"updated_by": "test_user"}}

        # Mock the HTTP response
        updated_invoice_data = {**sample_invoice_data, **update_data}
        mock_response = Mock()
        mock_http_client.put.return_value = (updated_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.update(debt_id, invoice_id, update_data)

        # Verify HTTP client was called correctly
        mock_http_client.put.assert_called_once_with(
            f"debts/{debt_id}/invoices/{invoice_id}", data=update_data, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)
        assert result.description == "Updated test invoice"

    def test_update_invoice_with_model(
        self, invoices_resource, mock_http_client, sample_invoice_data, sample_invoice_model
    ):
        """Test updating an invoice with Invoice model object."""
        debt_id = "debt_123"
        invoice_id = "inv_456"

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.put.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.update(debt_id, invoice_id, sample_invoice_model)

        # Verify HTTP client was called correctly
        expected_api_data = sample_invoice_model.to_api_body()
        mock_http_client.put.assert_called_once_with(
            f"debts/{debt_id}/invoices/{invoice_id}", data=expected_api_data, return_response=True
        )

        # Verify result
        assert isinstance(result, Invoice)

    def test_update_invoice_with_expand(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test updating an invoice with expand parameter."""
        debt_id = "debt_123"
        invoice_id = "inv_456"
        update_data = {"description": "Updated invoice"}
        expand = ["line_items"]

        # Mock the HTTP response
        mock_response = Mock()
        mock_http_client.put.return_value = (sample_invoice_data, mock_response)

        # Call the method
        result = invoices_resource.update(debt_id, invoice_id, update_data, expand=expand)

        # Verify HTTP client was called correctly
        mock_http_client.put.assert_called_once_with(
            f"debts/{debt_id}/invoices/{invoice_id}",
            data=update_data,
            params={"expand[]": expand},
            return_response=True,
        )

        # Verify result
        assert isinstance(result, Invoice)

    def test_search_invoices(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test searching invoices."""
        debt_id = "debt_123"
        query = "status:outstanding"
        limit = 10

        # Mock the HTTP response
        search_response = {"data": [sample_invoice_data], "has_more": False, "total_count": 1}
        mock_response = Mock()
        mock_http_client.get.return_value = (search_response, mock_response)

        # Call the method
        result = invoices_resource.search(debt_id, query, limit=limit)

        # Verify HTTP client was called correctly
        mock_http_client.get.assert_called_once_with(
            f"debts/{debt_id}/invoices/search", params={"query": query, "limit": limit}, return_response=True
        )

        # Verify result
        assert hasattr(result, "data")
        assert len(result.data) == 1

    def test_search_invoices_with_expand(self, invoices_resource, mock_http_client, sample_invoice_data):
        """Test searching invoices with expand parameter."""
        debt_id = "debt_123"
        query = "reference:INV-2024"
        expand = ["line_items"]

        # Mock the HTTP response
        search_response = {"data": [sample_invoice_data], "has_more": False, "total_count": 1}
        mock_response = Mock()
        mock_http_client.get.return_value = (search_response, mock_response)

        # Call the method
        result = invoices_resource.search(debt_id, query, expand=expand)

        # Verify HTTP client was called correctly
        mock_http_client.get.assert_called_once_with(
            f"debts/{debt_id}/invoices/search", params={"query": query, "expand[]": expand}, return_response=True
        )

        # Verify result
        assert hasattr(result, "data")

    def test_hasattr_check_for_model_objects(self, invoices_resource, sample_invoice_model):
        """Test that the hasattr check works correctly for model objects."""
        # Verify that Invoice model has to_api_body method
        assert hasattr(sample_invoice_model, "to_api_body")

        # Verify that dictionary doesn't have to_api_body method
        invoice_dict = {"reference": "INV-TEST", "description": "Test"}
        assert not hasattr(invoice_dict, "to_api_body")

    def test_model_to_api_body_conversion(self, sample_invoice_model):
        """Test that model to_api_body conversion works correctly."""
        api_body = sample_invoice_model.to_api_body()

        # Verify expected fields are present
        assert "reference" in api_body
        assert "description" in api_body
        assert "invoiced_on" in api_body
        assert "due_on" in api_body
        assert "status" in api_body
        assert "line_items" in api_body
        assert "metadata" in api_body

        # Verify server fields are excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # Verify dates are serialized as strings
        assert isinstance(api_body["invoiced_on"], str)
        assert isinstance(api_body["due_on"], str)

        # Verify line items are processed correctly
        assert isinstance(api_body["line_items"], list)
        assert len(api_body["line_items"]) == 2

        # Verify line item structure
        line_item = api_body["line_items"][0]
        assert "kind" in line_item
        assert "description" in line_item
        assert "amount" in line_item
        assert "currency" in line_item
        assert "transaction_at" in line_item
        assert "metadata" in line_item

        # Verify line item server fields are excluded
        assert "id" not in line_item
        assert "object" not in line_item


class TestInvoicesResourceErrorHandling:
    """Test error handling in InvoicesResource."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return MagicMock()

    @pytest.fixture
    def invoices_resource(self, mock_http_client):
        """Create an InvoicesResource instance with mock HTTP client."""
        return InvoicesResource(mock_http_client)

    def test_get_invoice_not_found(self, invoices_resource, mock_http_client):
        """Test handling of not found error when getting invoice."""
        debt_id = "debt_123"
        invoice_id = "nonexistent_invoice"

        # Mock HTTP client to raise NotFoundError
        mock_http_client.get.side_effect = NotFoundError(
            "Invoice not found", response_data={"error": "not_found", "message": "Invoice not found"}
        )

        # Call the method and expect exception
        with pytest.raises(NotFoundError) as exc_info:
            invoices_resource.get(debt_id, invoice_id)

        assert exc_info.value.status_code == 404
        assert "Invoice not found" in str(exc_info.value)

    def test_create_invoice_validation_error(self, invoices_resource, mock_http_client):
        """Test handling of validation error when creating invoice."""
        debt_id = "debt_123"
        invalid_invoice_data = {
            "reference": "",  # Invalid empty reference
            "line_items": [],  # Invalid empty line items
        }

        # Mock HTTP client to raise ValidationError
        mock_http_client.post.side_effect = ValidationError(
            "Validation failed",
            response_data={"errors": {"reference": ["cannot be blank"], "line_items": ["cannot be empty"]}},
        )

        # Call the method and expect exception
        with pytest.raises(ValidationError) as exc_info:
            invoices_resource.create(debt_id, invalid_invoice_data)

        assert exc_info.value.status_code == 422
        assert "Validation failed" in str(exc_info.value)

    def test_update_invoice_not_found(self, invoices_resource, mock_http_client):
        """Test handling of not found error when updating invoice."""
        debt_id = "debt_123"
        invoice_id = "nonexistent_invoice"
        update_data = {"description": "Updated description"}

        # Mock HTTP client to raise NotFoundError
        mock_http_client.put.side_effect = NotFoundError(
            "Invoice not found", response_data={"error": "not_found", "message": "Invoice not found"}
        )

        # Call the method and expect exception
        with pytest.raises(NotFoundError) as exc_info:
            invoices_resource.update(debt_id, invoice_id, update_data)

        assert exc_info.value.status_code == 404
        assert "Invoice not found" in str(exc_info.value)


class TestInvoicesResourceIntegration:
    """Integration-style tests for InvoicesResource."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return MagicMock()

    @pytest.fixture
    def invoices_resource(self, mock_http_client):
        """Create an InvoicesResource instance with mock HTTP client."""
        return InvoicesResource(mock_http_client)

    def test_full_invoice_lifecycle_with_models(self, invoices_resource, mock_http_client):
        """Test full invoice lifecycle using model objects."""
        debt_id = "debt_lifecycle_test"

        # Create invoice model
        invoice_model = Invoice(
            reference="INV-LIFECYCLE-001",
            description="Lifecycle test invoice",
            invoiced_on=date(2024, 1, 20),
            due_on=date(2024, 2, 20),
            status="outstanding",
            line_items=[
                LineItem(
                    kind=LineItemKind.DEBT,
                    description="Principal amount",
                    amount=15000,
                    currency=Currency.GBP,
                    transaction_at=datetime.now() - timedelta(hours=2),
                    metadata={"category": "principal", "priority": "high"},
                )
            ],
            metadata={"test_case": "lifecycle", "created_by": "test_suite"},
        )

        # Mock responses for create, get, and update
        created_invoice_data = {
            "id": "inv_lifecycle_123",
            "object": "invoice",
            "debt": debt_id,
            "reference": "INV-LIFECYCLE-001",
            "status": "outstanding",
            "description": "Lifecycle test invoice",
            "created_at": "2024-01-20T10:00:00Z",
            "updated_at": "2024-01-20T10:00:00Z",
        }

        updated_invoice_data = {**created_invoice_data, "status": "paid", "updated_at": "2024-01-21T10:00:00Z"}

        mock_response = Mock()
        mock_http_client.post.return_value = (created_invoice_data, mock_response)
        mock_http_client.get.return_value = (created_invoice_data, mock_response)
        mock_http_client.put.return_value = (updated_invoice_data, mock_response)

        # 1. Create invoice with model
        created_invoice = invoices_resource.create(debt_id, invoice_model, expand=["line_items"])
        assert isinstance(created_invoice, Invoice)
        assert created_invoice.id == "inv_lifecycle_123"

        # 2. Get invoice with expand
        retrieved_invoice = invoices_resource.get(debt_id, created_invoice.id, expand=["line_items"])
        assert isinstance(retrieved_invoice, Invoice)
        assert retrieved_invoice.id == created_invoice.id

        # 3. Update invoice with model
        updated_model = Invoice(
            reference="INV-LIFECYCLE-001",
            description="Updated lifecycle test invoice",
            status="paid",
            metadata={"test_case": "lifecycle", "updated_by": "test_suite"},
        )

        updated_invoice = invoices_resource.update(debt_id, created_invoice.id, updated_model, expand=["line_items"])
        assert isinstance(updated_invoice, Invoice)
        assert updated_invoice.status == "paid"

        # Verify all HTTP calls were made correctly
        assert mock_http_client.post.call_count == 1
        assert mock_http_client.get.call_count == 1
        assert mock_http_client.put.call_count == 1

    def test_mixed_data_types_support(self, invoices_resource, mock_http_client):
        """Test that resource supports both dict and model data types."""
        debt_id = "debt_mixed_test"

        # Test data
        dict_data = {"reference": "INV-DICT-001", "description": "Dictionary-based invoice", "status": "outstanding"}

        model_data = Invoice(reference="INV-MODEL-001", description="Model-based invoice", status="outstanding")

        mock_response_data = {"id": "inv_test", "object": "invoice", "reference": "INV-TEST", "status": "outstanding"}
        mock_response = Mock()
        mock_http_client.post.return_value = (mock_response_data, mock_response)

        # Test create with dict
        result1 = invoices_resource.create(debt_id, dict_data)
        assert isinstance(result1, Invoice)

        # Test create with model
        result2 = invoices_resource.create(debt_id, model_data)
        assert isinstance(result2, Invoice)

        # Verify both calls were made
        assert mock_http_client.post.call_count == 2

        # Verify first call used dict data directly
        first_call_args = mock_http_client.post.call_args_list[0]
        assert first_call_args[1]["data"] == dict_data

        # Verify second call used model's API body
        second_call_args = mock_http_client.post.call_args_list[1]
        expected_api_body = model_data.to_api_body()
        assert second_call_args[1]["data"] == expected_api_body
