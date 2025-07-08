"""
Unit tests for contact details resource.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import ContactDetail, PaginatedResponse
from ophelos_sdk.resources import ContactDetailsResource


class TestContactDetailsResource:
    """Test cases for contact details resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def contact_details_resource(self, mock_http_client):
        """Create contact details resource for testing."""
        return ContactDetailsResource(mock_http_client)

    @pytest.fixture
    def sample_contact_detail_data(self):
        """Sample contact detail data for testing."""
        return {
            "id": "cd_123456789",
            "object": "contact_detail",
            "type": "email",
            "value": "test@example.com",
            "primary": True,
            "usage": "permanent",
            "source": "client",
            "status": "active",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
            "metadata": {"verified": True},
        }

    def test_create_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test creating a contact detail."""
        create_data = {
            "type": "email",
            "value": "test@example.com",
            "primary": True,
            "usage": "permanent",
            "source": "client",
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.create("cust_123", create_data)

        mock_http_client.post.assert_called_once_with(
            "customers/cust_123/contact_details", data=create_data, return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.id == sample_contact_detail_data["id"]

    def test_create_contact_detail_with_expand(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test creating a contact detail with expand parameters."""
        create_data = {"type": "phone_number", "value": "+44123456789"}
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.create("cust_123", create_data, expand=["customer"])

        mock_http_client.post.assert_called_once_with(
            "customers/cust_123/contact_details",
            data=create_data,
            params={"expand[]": ["customer"]},
            return_response=True,
        )
        assert isinstance(result, ContactDetail)

    def test_create_contact_detail_with_model(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test creating a contact detail using ContactDetail model instance."""
        contact_detail = ContactDetail(type="email", value="model@example.com", primary=True, usage="permanent")
        mock_response = Mock()
        mock_response.status_code = 201
        mock_http_client.post.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.create("cust_123", contact_detail)

        # Should call to_api_body() on the model
        expected_data = contact_detail.to_api_body()
        mock_http_client.post.assert_called_once_with(
            "customers/cust_123/contact_details", data=expected_data, return_response=True
        )
        assert isinstance(result, ContactDetail)

    def test_update_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test updating a contact detail."""
        update_data = {"status": "verified", "primary": False}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.update("cust_123", "cd_123456789", update_data)

        mock_http_client.put.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", data=update_data, return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.id == sample_contact_detail_data["id"]

    def test_update_contact_detail_with_expand(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test updating a contact detail with expand parameters."""
        update_data = {"status": "inactive"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.update("cust_123", "cd_123456789", update_data, expand=["customer"])

        mock_http_client.put.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789",
            data=update_data,
            params={"expand[]": ["customer"]},
            return_response=True,
        )
        assert isinstance(result, ContactDetail)

    def test_update_contact_detail_with_model(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test updating a contact detail using ContactDetail model instance."""
        contact_detail = ContactDetail(type="email", value="updated@example.com", primary=False, status="verified")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.put.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.update("cust_123", "cd_123456789", contact_detail)

        # Should call to_api_body() on the model
        expected_data = contact_detail.to_api_body()
        mock_http_client.put.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", data=expected_data, return_response=True
        )
        assert isinstance(result, ContactDetail)

    def test_get_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test getting a specific contact detail."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.get("cust_123", "cd_123456789")

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", params={}, return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.id == sample_contact_detail_data["id"]

    def test_get_contact_detail_with_expand(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data
    ):
        """Test getting a contact detail with expand parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (sample_contact_detail_data, mock_response)

        result = contact_details_resource.get("cust_123", "cd_123456789", expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", params={"expand[]": ["customer"]}, return_response=True
        )
        assert isinstance(result, ContactDetail)

    def test_delete_contact_detail(self, contact_details_resource, mock_http_client, sample_contact_detail_data):
        """Test deleting (soft delete) a contact detail."""
        # Mock response with status "deleted"
        deleted_data = sample_contact_detail_data.copy()
        deleted_data["status"] = "deleted"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.delete.return_value = (deleted_data, mock_response)

        result = contact_details_resource.delete("cust_123", "cd_123456789")

        mock_http_client.delete.assert_called_once_with(
            "customers/cust_123/contact_details/cd_123456789", return_response=True
        )
        assert isinstance(result, ContactDetail)
        assert result.status == "deleted"

    def test_list_contact_details(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data, sample_paginated_response
    ):
        """Test listing contact details for a customer."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_contact_detail_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = contact_details_resource.list("cust_123", limit=20)

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details", params={"limit": 20}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], ContactDetail)

    def test_list_contact_details_with_pagination(
        self, contact_details_resource, mock_http_client, sample_contact_detail_data, sample_paginated_response
    ):
        """Test listing contact details with pagination parameters."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_contact_detail_data]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (mock_response_data, mock_response)

        result = contact_details_resource.list("cust_123", limit=10, after="cd_after_123", expand=["customer"])

        mock_http_client.get.assert_called_once_with(
            "customers/cust_123/contact_details",
            params={"limit": 10, "after": "cd_after_123", "expand[]": ["customer"]},
            return_response=True,
        )
        assert isinstance(result, PaginatedResponse)
