"""
Unit tests for customers resource.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import Customer, PaginatedResponse
from ophelos_sdk.resources import CustomersResource


class TestCustomersResource:
    """Test cases for customers resource."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def customers_resource(self, mock_http_client):
        """Create customers resource for testing."""
        return CustomersResource(mock_http_client)

    def test_list_customers(
        self, customers_resource, mock_http_client, sample_customer_data, sample_paginated_response
    ):
        """Test listing customers."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_customer_data]
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_get_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return mock_response_data, mock_response
            return mock_response_data

        mock_http_client.get.side_effect = mock_get_side_effect

        result = customers_resource.list(limit=10)

        mock_http_client.get.assert_called_once_with("customers", params={"limit": 10}, return_response=True)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Customer)

    def test_search_customers(
        self, customers_resource, mock_http_client, sample_customer_data, sample_paginated_response
    ):
        """Test searching customers."""
        mock_response_data = sample_paginated_response.copy()
        mock_response_data["data"] = [sample_customer_data]
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_get_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return mock_response_data, mock_response
            return mock_response_data

        mock_http_client.get.side_effect = mock_get_side_effect

        result = customers_resource.search("email:john@example.com")

        mock_http_client.get.assert_called_once_with(
            "customers/search", params={"query": "email:john@example.com"}, return_response=True
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert isinstance(result.data[0], Customer)

    def test_get_customer(self, customers_resource, mock_http_client, sample_customer_data):
        """Test getting a specific customer."""
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_get_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return sample_customer_data, mock_response
            return sample_customer_data

        mock_http_client.get.side_effect = mock_get_side_effect

        result = customers_resource.get("cust_123")

        mock_http_client.get.assert_called_once_with("customers/cust_123", params={}, return_response=True)
        assert isinstance(result, Customer)
        assert result.id == sample_customer_data["id"]

    def test_create_customer(self, customers_resource, mock_http_client, sample_customer_data):
        """Test creating a customer."""
        create_data = {"first_name": "John", "last_name": "Doe", "organisation_id": "org_123"}
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 201

        # Configure mock to return tuple when return_response=True
        def mock_post_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return sample_customer_data, mock_response
            return sample_customer_data

        mock_http_client.post.side_effect = mock_post_side_effect

        result = customers_resource.create(create_data)

        mock_http_client.post.assert_called_once_with("customers", data=create_data, return_response=True)
        assert isinstance(result, Customer)

    def test_update_customer(self, customers_resource, mock_http_client, sample_customer_data):
        """Test updating a customer."""
        update_data = {"phone": "+447700900123"}
        # Mock response object for _req_res functionality
        mock_response = Mock()
        mock_response.status_code = 200

        # Configure mock to return tuple when return_response=True
        def mock_put_side_effect(*args, **kwargs):
            if kwargs.get("return_response", False):
                return sample_customer_data, mock_response
            return sample_customer_data

        mock_http_client.put.side_effect = mock_put_side_effect

        result = customers_resource.update("cust_123", update_data)

        mock_http_client.put.assert_called_once_with("customers/cust_123", data=update_data, return_response=True)
        assert isinstance(result, Customer)
