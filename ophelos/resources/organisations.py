"""
Organisations resource manager for Ophelos API.
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource
from ..models import Organisation, Payment, PaginatedResponse


class OrganisationsResource(BaseResource):
    """Resource manager for organisation operations."""
    
    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List organisations.
        
        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with organisation data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_data = self.http_client.get("organisations", params=params)
        return self._parse_list_response(response_data, Organisation)
    
    def get(
        self,
        org_id: str,
        expand: Optional[List[str]] = None
    ) -> Organisation:
        """
        Get a specific organisation.
        
        Args:
            org_id: Organisation ID
            expand: List of fields to expand
            
        Returns:
            Organisation instance
        """
        params = self._build_expand_params(expand)
        response_data = self.http_client.get(f"organisations/{org_id}", params=params)
        return self._parse_response(response_data, Organisation)
    
    def create(self, data: Dict[str, Any]) -> Organisation:
        """
        Create a new organisation.
        
        Args:
            data: Organisation data
            
        Returns:
            Created organisation instance
        """
        response_data = self.http_client.post("organisations", data=data)
        return self._parse_response(response_data, Organisation)
    
    def update(self, org_id: str, data: Dict[str, Any]) -> Organisation:
        """
        Update an organisation.
        
        Args:
            org_id: Organisation ID
            data: Updated organisation data
            
        Returns:
            Updated organisation instance
        """
        response_data = self.http_client.put(f"organisations/{org_id}", data=data)
        return self._parse_response(response_data, Organisation)
    
    def create_contact_detail(self, org_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a contact detail for an organisation.
        
        Args:
            org_id: Organisation ID
            data: Contact detail data
            
        Returns:
            Created contact detail
        """
        return self.http_client.post(f"organisations/{org_id}/contact_details", data=data)
    
    def list_payments(
        self,
        org_id: str,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List payments for an organisation.
        
        Args:
            org_id: Organisation ID
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payment data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_data = self.http_client.get(f"organisations/{org_id}/payments", params=params)
        return self._parse_list_response(response_data, Payment)
    
    def search_payments(
        self,
        org_id: str,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        Search payments for an organisation.
        
        Args:
            org_id: Organisation ID
            query: Search query string
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payment data
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_data = self.http_client.get(f"organisations/{org_id}/payments/search", params=params)
        return self._parse_list_response(response_data, Payment) 