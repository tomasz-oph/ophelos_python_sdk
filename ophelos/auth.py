"""
Authentication module for OAuth2 client credentials flow.
"""

import time
from typing import Optional, Dict
import requests
from .exceptions import AuthenticationError


class OAuth2Authenticator:
    """Handles OAuth2 client credentials authentication for Ophelos API."""

    def __init__(
        self, client_id: str, client_secret: str, audience: str, environment: str = "development"
    ):
        """
        Initialize OAuth2 authenticator.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            audience: API audience/identifier
            environment: "staging" or "production"
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.environment = environment

        # Token storage
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

        # Auth0 URLs based on environment
        if environment == "production":
            self.token_url = "https://ophelos.eu.auth0.com/oauth/token"
        elif environment == "development":
            self.token_url = "https://ophelos-dev.eu.auth0.com/oauth/token"
        else:
            self.token_url = "https://ophelos-staging.eu.auth0.com/oauth/token"

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._is_token_valid():
            assert self._access_token is not None  # This is guaranteed by _is_token_valid
            return self._access_token

        return self._fetch_new_token()

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._access_token or not self._token_expires_at:
            return False

        # Add 60 second buffer before expiration
        return time.time() < (self._token_expires_at - 60)

    def _fetch_new_token(self) -> str:
        """
        Fetch a new access token from Auth0.

        Returns:
            New access token

        Raises:
            AuthenticationError: If token request fails
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.audience,
        }

        try:
            response = requests.post(
                self.token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()

        except requests.RequestException as e:
            raise AuthenticationError(
                f"Failed to request access token: {str(e)}", details={"token_url": self.token_url}
            )

        try:
            token_data = response.json()
        except ValueError as e:
            raise AuthenticationError(
                f"Invalid token response format: {str(e)}", response_data={"text": response.text}
            )

        # Validate required fields
        if "access_token" not in token_data:
            raise AuthenticationError("Missing access_token in response", response_data=token_data)

        # Store token and expiration time
        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        self._token_expires_at = time.time() + expires_in

        assert self._access_token is not None  # We just set it above
        return self._access_token

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated requests.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def invalidate_token(self) -> None:
        """Invalidate the current token, forcing a refresh on next request."""
        self._access_token = None
        self._token_expires_at = None
