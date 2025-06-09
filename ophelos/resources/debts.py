"""
Debts resource manager for Ophelos API.
"""

from typing import Optional, Dict, Any, List, Union
from .base import BaseResource
from ..models import Debt, Payment, PaginatedResponse


class DebtsResource(BaseResource):
    """Resource manager for debt operations."""
    
    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List debts.
        
        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand (e.g., ["customer", "payments"])
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with debt data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_data = self.http_client.get("debts", params=params)
        return self._parse_list_response(response_data, Debt)
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        Search debts.
        
        Args:
            query: Search query string (e.g., "status:paying AND updated_at>=2024-01-01")
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with debt data
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_data = self.http_client.get("debts/search", params=params)
        return self._parse_list_response(response_data, Debt)
    
    def get(
        self,
        debt_id: str,
        expand: Optional[List[str]] = None
    ) -> Debt:
        """
        Get a specific debt.
        
        Args:
            debt_id: Debt ID
            expand: List of fields to expand
            
        Returns:
            Debt instance
        """
        params = self._build_expand_params(expand)
        response_data = self.http_client.get(f"debts/{debt_id}", params=params)
        return self._parse_response(response_data, Debt)
    
    def create(self, data: Dict[str, Any]) -> Debt:
        """
        Create a new debt.
        
        Args:
            data: Debt data
            
        Returns:
            Created debt instance
        """
        response_data = self.http_client.post("debts", data=data)
        return self._parse_response(response_data, Debt)
    
    def update(self, debt_id: str, data: Dict[str, Any]) -> Debt:
        """
        Update a debt.
        
        Args:
            debt_id: Debt ID
            data: Updated debt data
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.put(f"debts/{debt_id}", data=data)
        return self._parse_response(response_data, Debt)
    
    def delete(self, debt_id: str) -> Dict[str, Any]:
        """
        Delete a debt.
        
        Args:
            debt_id: Debt ID
            
        Returns:
            Deletion response
        """
        return self.http_client.delete(f"debts/{debt_id}")
    
    def ready(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Mark debt as ready for processing.
        
        Args:
            debt_id: Debt ID
            data: Optional additional data
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/ready", data=data or {})
        return self._parse_response(response_data, Debt)
    
    def pause(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Pause debt processing.
        
        Args:
            debt_id: Debt ID
            data: Optional pause data (e.g., reason, until date)
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/pause", data=data or {})
        return self._parse_response(response_data, Debt)
    
    def resume(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Resume debt processing.
        
        Args:
            debt_id: Debt ID
            data: Optional resume data
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/resume", data=data or {})
        return self._parse_response(response_data, Debt)
    
    def withdraw(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Withdraw debt from processing.
        
        Args:
            debt_id: Debt ID
            data: Optional withdrawal data (e.g., reason)
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/withdraw", data=data or {})
        return self._parse_response(response_data, Debt)
    
    def dispute(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Mark debt as disputed.
        
        Args:
            debt_id: Debt ID
            data: Optional dispute data (e.g., reason, details)
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/dispute", data=data or {})
        return self._parse_response(response_data, Debt)
    
    def process_exhausted(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Mark debt as process exhausted.
        
        Args:
            debt_id: Debt ID
            data: Optional process exhausted data
            
        Returns:
            Updated debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/process_exhausted", data=data or {})
        return self._parse_response(response_data, Debt)
    
    def get_summary(self, debt_id: str) -> Dict[str, Any]:
        """
        Get debt summary.
        
        Args:
            debt_id: Debt ID
            
        Returns:
            Debt summary data
        """
        return self.http_client.get(f"debts/{debt_id}/summary")
    
    # Payment operations for debts
    def list_payments(
        self,
        debt_id: str,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        List payments for a debt.
        
        Args:
            debt_id: Debt ID
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payment data
        """
        params = self._build_list_params(limit, after, before, expand, **kwargs)
        response_data = self.http_client.get(f"debts/{debt_id}/payments", params=params)
        return self._parse_list_response(response_data, Payment)
    
    def search_payments(
        self,
        debt_id: str,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs
    ) -> PaginatedResponse:
        """
        Search payments for a debt.
        
        Args:
            debt_id: Debt ID
            query: Search query string
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters
            
        Returns:
            Paginated response with payment data
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_data = self.http_client.get(f"debts/{debt_id}/payments/search", params=params)
        return self._parse_list_response(response_data, Payment)
    
    def create_payment(self, debt_id: str, data: Dict[str, Any]) -> Payment:
        """
        Create a payment for a debt.
        
        Args:
            debt_id: Debt ID
            data: Payment data
            
        Returns:
            Created payment instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/payments", data=data)
        return self._parse_response(response_data, Payment)
    
    def get_payment(self, debt_id: str, payment_id: str) -> Payment:
        """
        Get a specific payment for a debt.
        
        Args:
            debt_id: Debt ID
            payment_id: Payment ID
            
        Returns:
            Payment instance
        """
        response_data = self.http_client.get(f"debts/{debt_id}/payments/{payment_id}")
        return self._parse_response(response_data, Payment)
    
    def update_payment(self, debt_id: str, payment_id: str, data: Dict[str, Any]) -> Payment:
        """
        Update a payment for a debt.
        
        Args:
            debt_id: Debt ID
            payment_id: Payment ID
            data: Updated payment data
            
        Returns:
            Updated payment instance
        """
        response_data = self.http_client.put(f"debts/{debt_id}/payments/{payment_id}", data=data)
        return self._parse_response(response_data, Payment) 