"""
Unit tests for resource error handling.
"""

from unittest.mock import Mock

import pytest

from ophelos_sdk.http_client import HTTPClient
from ophelos_sdk.models import Debt, PaginatedResponse
from ophelos_sdk.resources import DebtsResource


class TestResourceErrorHandling:
    """Test error handling in resource managers."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return Mock(spec=HTTPClient)

    @pytest.fixture
    def debts_resource(self, mock_http_client):
        """Create debts resource for testing."""
        return DebtsResource(mock_http_client)

    def test_parsing_fallback_on_error(self, debts_resource, mock_http_client):
        """Test that parsing falls back to raw data on error."""
        # Return invalid data that can't be parsed into a Debt model
        invalid_debt_data = {"invalid": "data", "missing_required_fields": True}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (invalid_debt_data, mock_response)

        result = debts_resource.get("debt_123")

        # Should return raw data instead of raising an error
        assert result == invalid_debt_data

    def test_list_parsing_fallback(self, debts_resource, mock_http_client):
        """Test that list parsing falls back to raw data on individual item errors."""
        # Mix of valid and invalid data
        response_data = {
            "object": "list",
            "data": [
                {  # Valid debt data
                    "id": "debt_123",
                    "object": "debt",
                    "status": {
                        "value": "prepared",
                        "whodunnit": "system",
                        "context": None,
                        "reason": None,
                        "updated_at": "2024-01-15T10:00:00Z",
                    },
                    "customer": "cust_123",
                    "organisation": "org_123",
                    "customer_id": "cust_123",
                    "organisation_id": "org_123",
                    "summary": {"amount_total": 10000, "amount_paid": 0, "amount_remaining": 10000},
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-15T10:00:00Z",
                },
                {"invalid": "data"},  # Invalid debt data
            ],
            "has_more": False,
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.get.return_value = (response_data, mock_response)

        result = debts_resource.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        # First item should be parsed as Debt
        assert isinstance(result.data[0], Debt)
        # Second item should remain as raw dict
        assert isinstance(result.data[1], dict)
        assert result.data[1] == {"invalid": "data"}

    def test_parse_error_debugging_interface(self, debts_resource):
        """Test that ParseError provides request/response debugging information."""
        from unittest.mock import Mock

        import requests

        from ophelos_sdk.exceptions import ParseError

        # Create a mock response object
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.test.com/debts"
        mock_response.reason = "OK"
        mock_response.encoding = "utf-8"

        # Mock the elapsed attribute
        mock_elapsed = Mock()
        mock_elapsed.total_seconds.return_value = 0.123
        mock_response.elapsed = mock_elapsed

        # Create a mock request
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = "https://api.test.com/debts"
        mock_request.headers = {"Authorization": "Bearer token"}
        mock_request.body = None
        mock_response.request = mock_request

        # Test ParseError with response object
        try:
            raise ParseError("Test parse error", response=mock_response)
        except ParseError as e:
            # Should have debugging interface
            assert e.request_info is not None
            assert e.request_info["method"] == "GET"
            assert e.request_info["url"] == "https://api.test.com/debts"
            assert e.request_info["headers"]["Authorization"] == "Bearer token"
            assert e.request_info["body"] is None

            assert e.response_info is not None
            assert e.response_info["status_code"] == 200
            assert e.response_info["headers"]["content-type"] == "application/json"
            assert e.response_info["url"] == "https://api.test.com/debts"
            assert e.response_info["reason"] == "OK"
            assert e.response_info["encoding"] == "utf-8"
            assert e.response_info["elapsed_ms"] == 123.0

            assert e.response_raw is mock_response

        # Test ParseError without response object (should be None)
        try:
            raise ParseError("Test parse error without response")
        except ParseError as e:
            assert e.request_info is None
            assert e.response_info is None
            assert e.response_raw is None

    def test_general_exception_handling_gap(self, debts_resource, mock_http_client):
        """Test what happens with general code processing errors (currently not handled)."""
        from unittest.mock import Mock

        import requests

        # Create a mock response object for context
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.test.com/debts"
        mock_response.reason = "OK"
        mock_response.encoding = "utf-8"

        mock_elapsed = Mock()
        mock_elapsed.total_seconds.return_value = 0.123
        mock_response.elapsed = mock_elapsed

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = "https://api.test.com/debts"
        mock_request.headers = {"Authorization": "Bearer token"}
        mock_request.body = None
        mock_response.request = mock_request

        # Simulate a general code error that occurs during request processing
        # This could be a programming error, unexpected network issue, etc.
        mock_http_client.get.side_effect = ValueError("Some unexpected error")

        # Currently, this will bubble up as a regular ValueError without debugging info
        try:
            debts_resource.get("debt_123")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            # This is the current behavior - no debugging interface
            assert str(e) == "Some unexpected error"
            # These would fail because ValueError doesn't have debugging interface
            assert not hasattr(e, "request_info")
            assert not hasattr(e, "response_info")
            assert not hasattr(e, "response_raw")

            # This shows the gap - we have no access to request/response context
            # that could help debug what went wrong

    def test_unexpected_error_debugging_interface(self):
        """Test that UnexpectedError provides request/response debugging information."""
        from unittest.mock import Mock, patch

        from ophelos_sdk.auth import StaticTokenAuthenticator
        from ophelos_sdk.exceptions import UnexpectedError
        from ophelos_sdk.http_client import HTTPClient

        # Create real HTTP client with mock authenticator
        auth = Mock(spec=StaticTokenAuthenticator)
        auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}

        http_client = HTTPClient(
            authenticator=auth,
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

        # Mock the session.request method to raise an unexpected error
        with patch("ophelos_sdk.http_client.HTTPClient._get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request.side_effect = ValueError("Some unexpected error")
            mock_get_session.return_value = mock_session

            # Now this should be wrapped in UnexpectedError with debugging info
            try:
                http_client.get("/debts/debt_123")
                assert False, "Expected UnexpectedError to be raised"
            except UnexpectedError as e:
                # Should have debugging interface
                assert e.request_info is not None
                assert e.request_info["method"] == "GET"
                assert e.request_info["url"] == "https://api.test.com/debts/debt_123"
                assert "Authorization" in e.request_info["headers"]
                assert e.request_info["body"] is None

                # Should have original error
                assert e.original_error is not None
                assert isinstance(e.original_error, ValueError)
                assert str(e.original_error) == "Some unexpected error"

                # Response info should be None for pre-request errors
                assert e.response_info is None
                assert e.response_raw is None

    def test_unexpected_error_response_processing(self):
        """Test that UnexpectedError handles response processing errors."""
        from unittest.mock import Mock, patch

        import requests

        from ophelos_sdk.auth import StaticTokenAuthenticator
        from ophelos_sdk.exceptions import UnexpectedError
        from ophelos_sdk.http_client import HTTPClient

        # Create real HTTP client with mock authenticator
        auth = Mock(spec=StaticTokenAuthenticator)
        auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}

        http_client = HTTPClient(
            authenticator=auth,
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

        # Mock successful request but error in response processing
        with patch("ophelos_sdk.http_client.HTTPClient._get_session") as mock_get_session:
            mock_session = Mock()
            mock_response = Mock(spec=requests.Response)
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.url = "https://api.test.com/debts/debt_123"
            mock_response.reason = "OK"
            mock_response.encoding = "utf-8"

            mock_elapsed = Mock()
            mock_elapsed.total_seconds.return_value = 0.123
            mock_response.elapsed = mock_elapsed

            mock_request = Mock()
            mock_request.method = "GET"
            mock_request.url = "https://api.test.com/debts/debt_123"
            mock_request.headers = {"Authorization": "Bearer test_token"}
            mock_request.body = None
            mock_response.request = mock_request

            # Simulate successful request
            mock_session.request.return_value = mock_response
            mock_get_session.return_value = mock_session

            # Mock response processing to raise an error
            with patch.object(http_client, "_handle_response") as mock_handle_response:
                mock_handle_response.side_effect = ValueError("Response processing error")

                try:
                    http_client.get("/debts/debt_123")
                    assert False, "Expected UnexpectedError to be raised"
                except UnexpectedError as e:
                    # Should have debugging interface with response info
                    assert e.request_info is not None
                    assert e.request_info["method"] == "GET"
                    assert e.request_info["url"] == "https://api.test.com/debts/debt_123"

                    # Should have response info since request succeeded
                    assert e.response_info is not None
                    assert e.response_info["status_code"] == 200
                    assert e.response_info["url"] == "https://api.test.com/debts/debt_123"
                    assert e.response_raw is mock_response

                    # Should have original error
                    assert e.original_error is not None
                    assert isinstance(e.original_error, ValueError)
                    assert str(e.original_error) == "Response processing error"
