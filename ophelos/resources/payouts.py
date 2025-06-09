"""
Payouts resource manager for Ophelos API.
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource
from ..models import Payout, PaginatedResponse


class PayoutsResource(BaseResource):
    """Resource manager for payout operations."""
    
    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List payouts.
        
        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payout data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_data = self.http_client.get("payouts", params=params)
        return self._parse_list_response(response_data, Payout)
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        Search payouts.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payout data
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_data = self.http_client.get("payouts/search", params=params)
        return self._parse_list_response(response_data, Payout)
    
    def get(
        self,
        payout_id: str,
        expand: Optional[List[str]] = None
    ) -> Payout:
        """
        Get a specific payout.
        
        Args:
            payout_id: Payout ID
            expand: List of fields to expand
            
        Returns:
            Payout instance
        """
        params = self._build_expand_params(expand)
        response_data = self.http_client.get(f"payouts/{payout_id}", params=params)
        return self._parse_response(response_data, Payout) 