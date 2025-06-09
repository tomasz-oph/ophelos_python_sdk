"""
Payment Plans resource manager for Ophelos API.
"""

from typing import Optional, Dict, Any, List
from .base import BaseResource
from ..models import PaymentPlan, PaginatedResponse


class PaymentPlansResource(BaseResource):
    """Resource manager for payment plan operations."""
    
    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List payment plans.
        
        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payment plan data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_data = self.http_client.get("payment_plans", params=params)
        return self._parse_list_response(response_data, PaymentPlan)
    
    def reschedule(self, plan_id: str, data: Dict[str, Any]) -> PaymentPlan:
        """
        Reschedule a payment plan.
        
        Args:
            plan_id: Payment plan ID
            data: Reschedule data (e.g., new dates, amounts)
            
        Returns:
            Updated payment plan instance
        """
        response_data = self.http_client.patch(f"payment_plans/{plan_id}/reschedule", data=data)
        return self._parse_response(response_data, PaymentPlan)
    
    def delay(self, plan_id: str, data: Dict[str, Any]) -> PaymentPlan:
        """
        Delay a payment plan.
        
        Args:
            plan_id: Payment plan ID
            data: Delay data (e.g., delay period, reason)
            
        Returns:
            Updated payment plan instance
        """
        response_data = self.http_client.patch(f"payment_plans/{plan_id}/delay", data=data)
        return self._parse_response(response_data, PaymentPlan) 