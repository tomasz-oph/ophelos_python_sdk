"""
Base resource class for Ophelos API resources.
"""

from typing import Optional, Dict, Any, List, Union, Type, TypeVar, cast
from ..http_client import HTTPClient
from ..models import BaseOphelosModel, PaginatedResponse

T = TypeVar("T", bound=BaseOphelosModel)


class BaseResource:
    """Base class for all API resource managers."""

    def __init__(self, http_client: HTTPClient):
        """
        Initialize base resource.

        Args:
            http_client: HTTP client instance for making requests
        """
        self.http_client = http_client

    def _build_expand_params(self, expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build expand parameters for API requests.

        Args:
            expand: List of fields to expand

        Returns:
            Dictionary with expand parameters
        """
        params: Dict[str, Any] = {}
        if expand:
            for i, field in enumerate(expand):
                params[f"expand[{i}]"] = field
        return params

    def _build_list_params(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build parameters for list requests.

        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Dictionary with query parameters
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["limit"] = limit
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        # Add expand parameters
        params.update(self._build_expand_params(expand))

        # Add additional parameters
        params.update(kwargs)

        return params

    def _build_search_params(
        self,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build parameters for search requests.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Dictionary with query parameters
        """
        params: Dict[str, Any] = {"query": query}

        if limit is not None:
            params["limit"] = limit

        # Add expand parameters
        params.update(self._build_expand_params(expand))

        # Add additional parameters
        params.update(kwargs)

        return params

    def _parse_response(
        self, response_data: Dict[str, Any], model_class: Optional[Type[T]] = None
    ) -> Union[T, Dict[str, Any]]:
        """
        Parse API response data into model instance.

        Args:
            response_data: Raw response data from API
            model_class: Pydantic model class to parse into

        Returns:
            Parsed model instance or raw data
        """
        if model_class and response_data:
            try:
                return model_class(**response_data)
            except Exception:
                # Fallback to raw data if parsing fails
                return response_data
        return response_data

    def _parse_model_response(self, response_data: Dict[str, Any], model_class: Type[T]) -> T:
        """
        Parse API response data into model instance, ensuring correct type.

        Args:
            response_data: Raw response data from API
            model_class: Pydantic model class to parse into

        Returns:
            Parsed model instance
        """
        result = self._parse_response(response_data, model_class)
        return cast(T, result)

    def _parse_list_response(
        self, response_data: Dict[str, Any], model_class: Optional[Type[BaseOphelosModel]] = None
    ) -> PaginatedResponse:
        """
        Parse paginated list response.

        Args:
            response_data: Raw response data from API
            model_class: Pydantic model class for list items

        Returns:
            Paginated response with parsed items
        """
        if not response_data:
            return PaginatedResponse(data=[])

        items = response_data.get("data", [])

        if model_class:
            parsed_items = []
            for item in items:
                try:
                    parsed_items.append(model_class(**item))
                except Exception:
                    # Fallback to raw data if parsing fails
                    parsed_items.append(item)
            response_data["data"] = parsed_items

        return PaginatedResponse(**response_data)
