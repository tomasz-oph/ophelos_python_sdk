"""
Pytest configuration and shared fixtures for Ophelos SDK tests.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date
import json

from ophelos import OphelosClient
from ophelos.auth import OAuth2Authenticator
from ophelos.http_client import HTTPClient


@pytest.fixture
def mock_auth_response():
    """Mock OAuth2 token response."""
    return {
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600
    }


@pytest.fixture
def mock_authenticator(mock_auth_response):
    """Mock OAuth2 authenticator."""
    authenticator = Mock(spec=OAuth2Authenticator)
    authenticator.get_access_token.return_value = mock_auth_response["access_token"]
    authenticator.get_auth_headers.return_value = {
        "Authorization": f"Bearer {mock_auth_response['access_token']}"
    }
    return authenticator


@pytest.fixture
def mock_http_client():
    """Mock HTTP client."""
    client = Mock(spec=HTTPClient)
    return client


@pytest.fixture
def sample_debt_data():
    """Sample debt data for testing."""
    return {
        "id": "debt_123456789",
        "object": "debt",
        "account_number": "ACC-001",
        "reference_code": "REF-001",
        "total_amount": 10000,
        "currency": "GBP",
        "status": "prepared",
        "kind": "purchased",
        "start_at": date.today().isoformat(),
        "customer_id": "cust_123456789",
        "organisation_id": "org_123456789",
        "metadata": {
            "case_id": "12345",
            "original_creditor": "Test Corp"
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "id": "cust_123456789",
        "object": "customer",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "country_code": "GB",
        "postal_code": "SW1A 1AA",
        "organisation_id": "org_123456789",
        "metadata": {
            "external_id": "customer_001"
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing."""
    return {
        "id": "pay_123456789",
        "object": "payment",
        "amount": 5000,
        "currency": "GBP",
        "status": "succeeded",
        "payment_provider": "stripe",
        "transaction_ref": "txn_12345",
        "transaction_at": datetime.now().isoformat(),
        "debt_id": "debt_123456789",
        "organisation_id": "org_123456789",
        "customer_id": "cust_123456789",
        "metadata": {
            "external_ref": "EXT-123"
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_paginated_response():
    """Sample paginated response structure."""
    return {
        "object": "list",
        "data": [],
        "has_more": False,
        "total_count": 0
    }


@pytest.fixture
def sample_webhook_event():
    """Sample webhook event data."""
    return {
        "id": "evt_123456789",
        "object": "event",
        "type": "debt.created",
        "created_at": datetime.now().isoformat(),
        "livemode": False,
        "data": {
            "id": "debt_123456789",
            "object": "debt",
            "status": "prepared",
            "total_amount": 10000
        }
    }


@pytest.fixture
def test_client_config():
    """Test client configuration."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "audience": "test_audience",
        "environment": "staging"
    }


@pytest.fixture
def ophelos_client(test_client_config, mock_authenticator, mock_http_client):
    """Mock Ophelos client for testing."""
    with patch('ophelos.client.OAuth2Authenticator', return_value=mock_authenticator), \
         patch('ophelos.client.HTTPClient', return_value=mock_http_client):
        return OphelosClient(**test_client_config)


@pytest.fixture
def mock_requests_session():
    """Mock requests session."""
    session = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"access_token": "test_token", "expires_in": 3600}
    response.content = b'{"test": "data"}'
    session.post.return_value = response
    session.get.return_value = response
    session.put.return_value = response
    session.patch.return_value = response
    session.delete.return_value = response
    return session 