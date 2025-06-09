"""
Tenants resource manager for Ophelos API.
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource
from ..models import Tenant


class TenantsResource(BaseResource):
    """Resource manager for tenant operations."""
    
    def get_me(self) -> Tenant:
        """
        Get my tenant information.
        
        Returns:
            Current tenant instance
        """
        response_data = self.http_client.get("tenants/me")
        return self._parse_response(response_data, Tenant)
    
    def update_me(self, data: Dict[str, Any]) -> Tenant:
        """
        Update my tenant information.
        
        Args:
            data: Updated tenant data
            
        Returns:
            Updated tenant instance
        """
        response_data = self.http_client.put("tenants/me", data=data)
        return self._parse_response(response_data, Tenant) 