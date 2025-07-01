"""
Pytest configuration and shared fixtures for Ophelos SDK tests.
"""

from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest

from ophelos_sdk import OphelosClient
from ophelos_sdk.auth import OAuth2Authenticator
from ophelos_sdk.http_client import HTTPClient


@pytest.fixture
def mock_auth_response():
    """Mock OAuth2 token response."""
    return {"access_token": "mock_access_token_12345", "token_type": "Bearer", "expires_in": 3600}


@pytest.fixture
def mock_authenticator(mock_auth_response):
    """Mock OAuth2 authenticator."""
    authenticator = Mock(spec=OAuth2Authenticator)
    authenticator.get_access_token.return_value = mock_auth_response["access_token"]
    authenticator.get_auth_headers.return_value = {"Authorization": f"Bearer {mock_auth_response['access_token']}"}
    return authenticator


@pytest.fixture
def mock_http_client():
    """Mock HTTP client."""
    client = Mock(spec=HTTPClient)
    return client


@pytest.fixture
def sample_debt_data():
    """Sample debt data for testing."""
    created_at = datetime.now().isoformat()
    updated_at = datetime.now().isoformat()
    return {
        "id": "debt_123456789",
        "object": "debt",
        "account_number": "ACC-001",
        "currency": "GBP",
        "status": {
            "value": "prepared",
            "whodunnit": "system",
            "context": None,
            "reason": None,
            "updated_at": updated_at,
        },
        "kind": "purchased",
        "start_at": date.today().isoformat(),
        "customer": "cust_123456789",
        "organisation": "org_123456789",
        "summary": {
            "amount_total": 10000,
            "amount_paid": 0,
            "amount_remaining": 10000,
            "breakdown": {
                "principal": 10000,
                "interest": 0,
                "fees": 0,
                "discounts": 0,
                "charges": 0,
                "value_added_tax": 0,
                "miscellaneous": 0,
                "refunds": 0,
            },
            "history": [],
            "created_at": created_at,
            "updated_at": updated_at,
        },
        "invoices": [],
        "line_items": [],
        "payments": [],
        "payment_plans": [],
        "tags": [],
        "configurations": {},
        "calculated_configurations": {},
        "originator": None,
        "metadata": {"case_id": "12345", "original_creditor": "Test Corp"},
        "created_at": created_at,
        "updated_at": updated_at,
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    created_at = datetime.now().isoformat()
    updated_at = datetime.now().isoformat()
    return {
        "id": "cust_123456789",
        "object": "customer",
        "kind": "unknown",
        "full_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "preferred_locale": "en",
        "date_of_birth": None,
        "contact_details": ["ccd_123456789"],  # List of contact detail IDs
        "debts": ["debt_123456789"],  # List of debt IDs
        "created_at": created_at,
        "updated_at": updated_at,
        "metadata": {"external_id": "customer_001"},
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
        "debt": "debt_123456789",
        "metadata": {"external_ref": "EXT-123"},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_paginated_response():
    """Sample paginated response structure."""
    return {"object": "list", "data": [], "has_more": False, "total_count": 0}


@pytest.fixture
def sample_webhook_event():
    """Sample webhook event data."""
    created_at = datetime.now().isoformat()
    return {
        "id": "evt_123456789",
        "object": "event",
        "type": "debt.created",
        "created_at": created_at,
        "livemode": False,
        "data": {
            "id": "debt_123456789",
            "object": "debt",
            "status": {
                "value": "prepared",
                "whodunnit": "system",
                "context": None,
                "reason": None,
                "updated_at": created_at,
            },
            "summary": {"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
        },
    }


@pytest.fixture
def test_client_config():
    """Test client configuration."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "audience": "test_audience",
        "environment": "staging",
    }


@pytest.fixture
def ophelos_client(test_client_config, mock_authenticator, mock_http_client):
    """Mock Ophelos client for testing."""
    with patch("ophelos_sdk.client.OAuth2Authenticator", return_value=mock_authenticator), patch(
        "ophelos_sdk.client.HTTPClient", return_value=mock_http_client
    ):
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
