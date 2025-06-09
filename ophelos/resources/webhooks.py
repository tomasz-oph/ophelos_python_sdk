"""
Webhooks resource manager for Ophelos API.
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource
from ..models import Webhook, PaginatedResponse


class WebhooksResource(BaseResource):
    """Resource manager for webhook operations."""
    
    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List webhooks.
        
        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with webhook data
        """
        params = self._build_list_params(limit, after, before, None, **kwargs)
        response_data = self.http_client.get("webhooks", params=params)
        return self._parse_list_response(response_data, Webhook)
    
    def get(self, webhook_id: str) -> Webhook:
        """
        Get a specific webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            Webhook instance
        """
        response_data = self.http_client.get(f"webhooks/{webhook_id}")
        return self._parse_response(response_data, Webhook)
    
    def create(self, data: Dict[str, Any]) -> Webhook:
        """
        Create a new webhook.
        
        Args:
            data: Webhook data (url, events, etc.)
            
        Returns:
            Created webhook instance
        """
        response_data = self.http_client.post("webhooks", data=data)
        return self._parse_response(response_data, Webhook)
    
    def update(self, webhook_id: str, data: Dict[str, Any]) -> Webhook:
        """
        Update a webhook.
        
        Args:
            webhook_id: Webhook ID
            data: Updated webhook data
            
        Returns:
            Updated webhook instance
        """
        response_data = self.http_client.put(f"webhooks/{webhook_id}", data=data)
        return self._parse_response(response_data, Webhook)
    
    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """
        Delete a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            Deletion response
        """
        return self.http_client.delete(f"webhooks/{webhook_id}") 