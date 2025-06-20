"""
Unit tests for Ophelos SDK HTTP client.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from urllib3.util.retry import Retry
from urllib3.response import HTTPResponse

from ophelos_sdk.http_client import HTTPClient, JitteredRetry
from ophelos_sdk.auth import OAuth2Authenticator
from ophelos_sdk.exceptions import (
    OphelosAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ConflictError,
    ForbiddenError,
    ServerError,
)


class TestHTTPClient:
    """Test cases for HTTP client."""

    @pytest.fixture
    def mock_authenticator(self):
        """Mock authenticator for testing."""
        auth = Mock(spec=OAuth2Authenticator)
        auth.get_auth_headers.return_value = {"Authorization": "Bearer test_token"}
        return auth

    @pytest.fixture
    def http_client(self, mock_authenticator):
        """Create HTTP client for testing."""
        return HTTPClient(
            authenticator=mock_authenticator,
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3,
        )

    def test_http_client_initialization(self, http_client, mock_authenticator):
        """Test HTTP client initialization."""
        assert http_client.authenticator == mock_authenticator
        assert http_client.base_url == "https://api.test.com"
        assert http_client.timeout == 30

    def test_prepare_headers(self, http_client):
        """Test header preparation."""
        headers = http_client._prepare_headers()

        expected_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ophelos-python-sdk/1.0.2",
            "Authorization": "Bearer test_token",
        }

        assert headers == expected_headers

    def test_prepare_headers_with_custom_headers(self, http_client):
        """Test header preparation with custom headers."""
        custom_headers = {"X-Custom-Header": "custom_value"}
        headers = http_client._prepare_headers(custom_headers)

        assert headers["X-Custom-Header"] == "custom_value"
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Content-Type"] == "application/json"

    @patch("requests.Session.get")
    def test_successful_get_request(self, mock_get, http_client):
        """Test successful GET request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_123", "status": "success"}
        mock_response.content = b'{"test": "data"}'
        mock_get.return_value = mock_response

        result = http_client.get("/test/endpoint", params={"limit": 10})

        assert result == {"id": "test_123", "status": "success"}
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://api.test.com/test/endpoint"
        assert call_args[1]["params"] == {"limit": 10}

    @patch("requests.Session.post")
    def test_successful_post_request(self, mock_post, http_client):
        """Test successful POST request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new_123", "created": True}
        mock_response.content = b'{"test": "data"}'
        mock_post.return_value = mock_response

        data = {"name": "Test Object"}
        result = http_client.post("/test/endpoint", data=data)

        assert result == {"id": "new_123", "created": True}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"] == data

    @patch("requests.Session.put")
    def test_successful_put_request(self, mock_put, http_client):
        """Test successful PUT request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_123", "updated": True}
        mock_response.content = b'{"test": "data"}'
        mock_put.return_value = mock_response

        data = {"name": "Updated Object"}
        result = http_client.put("/test/endpoint/123", data=data)

        assert result == {"id": "test_123", "updated": True}

    @patch("requests.Session.patch")
    def test_successful_patch_request(self, mock_patch, http_client):
        """Test successful PATCH request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_123", "patched": True}
        mock_response.content = b'{"test": "data"}'
        mock_patch.return_value = mock_response

        data = {"status": "updated"}
        result = http_client.patch("/test/endpoint/123", data=data)

        assert result == {"id": "test_123", "patched": True}

    @patch("requests.Session.delete")
    def test_successful_delete_request(self, mock_delete, http_client):
        """Test successful DELETE request."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_response.content = b""
        mock_delete.return_value = mock_response

        result = http_client.delete("/test/endpoint/123")

        assert result == {}

    def test_error_handling_401_authentication_error(self, http_client, mock_authenticator):
        """Test handling of 401 authentication errors."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Unauthorized"}
            mock_response.content = b'{"message": "Unauthorized"}'
            mock_get.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Unauthorized" in str(exc_info.value)
            # Should invalidate token on 401
            mock_authenticator.invalidate_token.assert_called_once()

    def test_error_handling_403_forbidden_error(self, http_client):
        """Test handling of 403 forbidden errors."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.json.return_value = {"message": "Forbidden"}
            mock_response.content = b'{"message": "Forbidden"}'
            mock_get.return_value = mock_response

            with pytest.raises(ForbiddenError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Forbidden" in str(exc_info.value)

    def test_error_handling_404_not_found_error(self, http_client):
        """Test handling of 404 not found errors."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"message": "Not Found"}
            mock_response.content = b'{"message": "Not Found"}'
            mock_get.return_value = mock_response

            with pytest.raises(NotFoundError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Not Found" in str(exc_info.value)

    def test_error_handling_409_conflict_error(self, http_client):
        """Test handling of 409 conflict errors."""
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 409
            mock_response.json.return_value = {"message": "Conflict"}
            mock_response.content = b'{"message": "Conflict"}'
            mock_post.return_value = mock_response

            with pytest.raises(ConflictError) as exc_info:
                http_client.post("/test/endpoint", data={})

            assert "Conflict" in str(exc_info.value)

    def test_error_handling_422_validation_error(self, http_client):
        """Test handling of 422 validation errors."""
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 422
            mock_response.json.return_value = {
                "message": "Validation failed",
                "errors": {"field": ["is required"]},
            }
            mock_response.content = b'{"message": "Validation failed"}'
            mock_post.return_value = mock_response

            with pytest.raises(ValidationError) as exc_info:
                http_client.post("/test/endpoint", data={})

            assert "Validation failed" in str(exc_info.value)

    def test_error_handling_429_rate_limit_error(self, http_client):
        """Test handling of 429 rate limit errors."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"message": "Too Many Requests"}
            mock_response.content = b'{"message": "Too Many Requests"}'
            mock_get.return_value = mock_response

            with pytest.raises(RateLimitError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Too Many Requests" in str(exc_info.value)

    def test_error_handling_500_server_error(self, http_client):
        """Test handling of 500 server errors."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"message": "Internal Server Error"}
            mock_response.content = b'{"message": "Internal Server Error"}'
            mock_get.return_value = mock_response

            with pytest.raises(ServerError) as exc_info:
                http_client.get("/test/endpoint")

            assert "Internal Server Error" in str(exc_info.value)
            assert exc_info.value.status_code == 500

    def test_error_handling_generic_4xx_error(self, http_client):
        """Test handling of generic 4xx errors."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 418  # I'm a teapot
            mock_response.json.return_value = {"message": "I'm a teapot"}
            mock_response.content = b'{"message": "I\'m a teapot"}'
            mock_get.return_value = mock_response

            with pytest.raises(OphelosAPIError) as exc_info:
                http_client.get("/test/endpoint")

            assert "I'm a teapot" in str(exc_info.value)
            assert exc_info.value.status_code == 418

    def test_response_without_json_content(self, http_client):
        """Test handling of responses without JSON content."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b""  # No content
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response

            result = http_client.get("/test/endpoint")
            assert result == {}

    def test_response_with_invalid_json(self, http_client):
        """Test handling of responses with invalid JSON."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = "Invalid response text"
            mock_response.content = b"invalid json"
            mock_get.return_value = mock_response

            with pytest.raises(OphelosAPIError) as exc_info:
                http_client.get("/test/endpoint")

            # Should use response text as message
            assert "Invalid response text" in str(exc_info.value)

    def test_base_url_path_handling(self, http_client):
        """Test proper handling of base URL and path combinations."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_get.return_value = mock_response

            # Test various path formats
            test_cases = [
                ("/test/endpoint", "https://api.test.com/test/endpoint"),
                ("test/endpoint", "https://api.test.com/test/endpoint"),
                ("/test/endpoint/", "https://api.test.com/test/endpoint/"),
                ("test/endpoint/", "https://api.test.com/test/endpoint/"),
            ]

            for path, expected_url in test_cases:
                http_client.get(path)
                call_args = mock_get.call_args
                # Should result in proper URL
                assert call_args[0][0] == expected_url

    def test_timeout_configuration(self, mock_authenticator):
        """Test timeout configuration."""
        client = HTTPClient(
            authenticator=mock_authenticator, base_url="https://api.test.com", timeout=60
        )

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_get.return_value = mock_response

            client.get("/test")

            call_args = mock_get.call_args
            assert call_args[1]["timeout"] == 60

    def test_tenant_id_header(self, mock_authenticator):
        """Test that OPHELOS_TENANT_ID header is added when tenant_id is set."""
        tenant_id = "test-tenant-123"
        client = HTTPClient(
            authenticator=mock_authenticator, base_url="https://api.test.com", tenant_id=tenant_id
        )

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_get.return_value = mock_response

            client.get("/test")

            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert "OPHELOS_TENANT_ID" in headers
            assert headers["OPHELOS_TENANT_ID"] == tenant_id

    def test_no_tenant_id_header_when_not_set(self, mock_authenticator):
        """Test that OPHELOS_TENANT_ID header is not added when tenant_id is None."""
        client = HTTPClient(
            authenticator=mock_authenticator, base_url="https://api.test.com", tenant_id=None
        )

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            mock_get.return_value = mock_response

            client.get("/test")

            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert "OPHELOS_TENANT_ID" not in headers

    def test_tenant_id_header_with_post_request(self, mock_authenticator):
        """Test that OPHELOS_TENANT_ID header is added for POST requests."""
        tenant_id = "test-tenant-456"
        client = HTTPClient(
            authenticator=mock_authenticator, base_url="https://api.test.com", tenant_id=tenant_id
        )

        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "123"}
            mock_response.content = b'{"id": "123"}'
            mock_post.return_value = mock_response

            client.post("/test", data={"name": "test"})

            call_args = mock_post.call_args
            headers = call_args[1]["headers"]
            assert "OPHELOS_TENANT_ID" in headers
            assert headers["OPHELOS_TENANT_ID"] == tenant_id


class TestJitteredRetry:
    """Test cases for JitteredRetry functionality."""

    def _create_mock_response(self, status=500):
        """Create a mock response object for retry history."""
        response = Mock()
        response.redirect_location = None
        response.status = status
        return response

    def test_jittered_retry_initialization(self):
        """Test JitteredRetry can be initialized properly."""
        retry = JitteredRetry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        assert retry.total == 3
        assert retry.status_forcelist == [429, 500, 502, 503, 504]
        assert retry.allowed_methods == ["HEAD", "GET", "OPTIONS"]
        assert retry.backoff_factor == 1

    def test_jittered_retry_inherits_from_retry(self):
        """Test JitteredRetry properly inherits from urllib3 Retry."""
        retry = JitteredRetry(total=3)
        assert isinstance(retry, Retry)
        assert isinstance(retry, JitteredRetry)

    def test_jittered_backoff_adds_randomness(self):
        """Test that jittered retry adds 0-1.5 seconds to base backoff."""
        jittered_retry = JitteredRetry(total=3, backoff_factor=1)

        # Test first retry (base: 0s, should be 0)
        jittered_retry.history = [self._create_mock_response()]
        jitter_time_1 = jittered_retry.get_backoff_time()

        assert jitter_time_1 == 0, f"Expected 0 for first retry, got {jitter_time_1}"

        # Test second retry (base: 2.0s, should be 2.0-3.5s)
        jittered_retry.history = [self._create_mock_response(), self._create_mock_response()]
        jitter_time_2 = jittered_retry.get_backoff_time()

        assert 2.0 <= jitter_time_2 <= 3.5, f"Expected 2.0-3.5, got {jitter_time_2}"

        # Test third retry (base: 4.0s, should be 4.0-5.5s)
        jittered_retry.history = [
            self._create_mock_response(),
            self._create_mock_response(),
            self._create_mock_response(),
        ]
        jitter_time_3 = jittered_retry.get_backoff_time()

        assert 4.0 <= jitter_time_3 <= 5.5, f"Expected 4.0-5.5, got {jitter_time_3}"

    def test_jitter_randomness_variation(self):
        """Test that jitter actually produces different values."""
        jittered_retry = JitteredRetry(total=3, backoff_factor=1)

        # Use second retry attempt (history length 2) which has non-zero base backoff
        times = []
        for _ in range(10):
            # Set history for second retry (base: 2.0s, should be 2.0-3.5s)
            jittered_retry.history = [self._create_mock_response(), self._create_mock_response()]
            time = jittered_retry.get_backoff_time()
            times.append(time)

        # All times should be in valid range for second retry
        for time in times:
            assert 2.0 <= time <= 3.5, f"Time {time} outside expected range 2.0-3.5"

        # Should have some variation (not all the same)
        unique_times = set(times)
        assert len(unique_times) > 1, "Jitter should produce varying times, got all same values"

        # Check that we're getting reasonable spread
        min_time = min(times)
        max_time = max(times)
        time_range = max_time - min_time
        assert time_range > 0.1, f"Expected more variation, got range: {time_range}"

    def test_zero_backoff_handling(self):
        """Test handling of zero or negative backoff times."""
        jittered_retry = JitteredRetry(total=3, backoff_factor=0)

        # With backoff_factor=0, base backoff should be 0
        jittered_retry.history = [self._create_mock_response()]
        backoff_time = jittered_retry.get_backoff_time()

        # Should return 0 when base backoff is 0
        assert backoff_time == 0

    def test_http_client_uses_jittered_retry(self, mock_authenticator):
        """Test that HTTPClient uses JitteredRetry by default."""
        client = HTTPClient(
            authenticator=mock_authenticator, base_url="https://api.test.com", max_retries=3
        )

        # Check that the session has the adapter with JitteredRetry
        assert hasattr(client.session, "adapters")

        # Get the adapter (should be for both http and https)
        adapters = client.session.adapters
        assert len(adapters) >= 2  # Should have http:// and https:// adapters

        # Check one of the adapters
        adapter = next(iter(adapters.values()))
        assert hasattr(adapter, "max_retries")
        assert isinstance(adapter.max_retries, JitteredRetry)

    def test_jitter_preserves_retry_configuration(self):
        """Test that jitter doesn't interfere with other retry settings."""
        jittered_retry = JitteredRetry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2,  # Different backoff factor
        )

        # Verify all settings are preserved
        assert jittered_retry.total == 5
        assert jittered_retry.status_forcelist == [429, 500, 502, 503, 504]
        assert jittered_retry.allowed_methods == ["HEAD", "GET", "OPTIONS"]
        assert jittered_retry.backoff_factor == 2

        # Test backoff with different factor (use second retry which has base 4.0)
        jittered_retry.history = [self._create_mock_response(), self._create_mock_response()]
        backoff_time = jittered_retry.get_backoff_time()

        # With backoff_factor=2, second retry base is 4.0, so jittered should be 4.0-5.5
        assert (
            4.0 <= backoff_time <= 5.5
        ), f"Expected 4.0-5.5 with backoff_factor=2, got {backoff_time}"
