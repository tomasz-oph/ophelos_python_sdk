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
        **kwargs: Any,
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
        **kwargs: Any,
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

    def get(self, debt_id: str, expand: Optional[List[str]] = None) -> Debt:
        """
        Get a specific debt by ID.

        Args:
            debt_id: Debt ID
            expand: List of fields to expand

        Returns:
            Debt instance
        """
        params = self._build_expand_params(expand)
        response_data = self.http_client.get(f"debts/{debt_id}", params=params)
        return self._parse_model_response(response_data, Debt)

    def create(self, data: Dict[str, Any], expand: Optional[List[str]] = None) -> Debt:
        """
        Create a new debt.

        Args:
            data: Debt data
            expand: List of fields to expand

        Returns:
            Created debt instance
        """
        if expand:
            params = self._build_expand_params(expand)
            response_data = self.http_client.post("debts", data=data, params=params)
        else:
            response_data = self.http_client.post("debts", data=data)
        return self._parse_model_response(response_data, Debt)

    def update(
        self, debt_id: str, data: Dict[str, Any], expand: Optional[List[str]] = None
    ) -> Debt:
        """
        Update a debt.

        Args:
            debt_id: Debt ID
            data: Updated debt data
            expand: List of fields to expand

        Returns:
            Updated debt instance
        """
        if expand:
            params = self._build_expand_params(expand)
            response_data = self.http_client.put(f"debts/{debt_id}", data=data, params=params)
        else:
            response_data = self.http_client.put(f"debts/{debt_id}", data=data)
        return self._parse_model_response(response_data, Debt)

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
        return self._parse_model_response(response_data, Debt)

    def pause(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Pause a debt.

        Args:
            debt_id: Debt ID
            data: Optional pause data

        Returns:
            Paused debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/pause", data=data or {})
        return self._parse_model_response(response_data, Debt)

    def resume(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Resume a debt.

        Args:
            debt_id: Debt ID
            data: Optional resume data

        Returns:
            Resumed debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/resume", data=data or {})
        return self._parse_model_response(response_data, Debt)

    def settle(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Settle a debt.

        Args:
            debt_id: Debt ID
            data: Optional settlement data

        Returns:
            Settled debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/settle", data=data or {})
        return self._parse_model_response(response_data, Debt)

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
        return self._parse_model_response(response_data, Debt)

    def dispute(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Mark a debt as disputed.

        Args:
            debt_id: Debt ID
            data: Optional dispute data

        Returns:
            Disputed debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/dispute", data=data or {})
        return self._parse_model_response(response_data, Debt)

    def resolve_dispute(self, debt_id: str, data: Optional[Dict[str, Any]] = None) -> Debt:
        """
        Resolve a debt dispute.

        Args:
            debt_id: Debt ID
            data: Optional resolution data

        Returns:
            Resolved debt instance
        """
        response_data = self.http_client.post(f"debts/{debt_id}/resolve-dispute", data=data or {})
        return self._parse_model_response(response_data, Debt)

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
    ) -> PaginatedResponse:
        """
        List payments for a debt.

        Args:
            debt_id: Debt ID
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand

        Returns:
            Paginated list of payments
        """
        params = self._build_list_params(limit, after, before, expand)
        response_data = self.http_client.get(f"debts/{debt_id}/payments", params=params)
        return self._parse_list_response(response_data, Payment)

    def search_payments(
        self,
        debt_id: str,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
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

    def create_payment(
        self, debt_id: str, data: Dict[str, Any], expand: Optional[List[str]] = None
    ) -> Payment:
        """
        Create a payment for a debt.

        Args:
            debt_id: Debt ID
            data: Payment data
            expand: List of fields to expand

        Returns:
            Created payment instance
        """
        if expand:
            params = self._build_expand_params(expand)
            response_data = self.http_client.post(
                f"debts/{debt_id}/payments", data=data, params=params
            )
        else:
            response_data = self.http_client.post(f"debts/{debt_id}/payments", data=data)
        return self._parse_model_response(response_data, Payment)

    def get_payment(
        self, debt_id: str, payment_id: str, expand: Optional[List[str]] = None
    ) -> Payment:
        """
        Get a specific payment for a debt.

        Args:
            debt_id: Debt ID
            payment_id: Payment ID
            expand: List of fields to expand

        Returns:
            Payment instance
        """
        if expand:
            params = self._build_expand_params(expand)
            response_data = self.http_client.get(
                f"debts/{debt_id}/payments/{payment_id}", params=params
            )
        else:
            response_data = self.http_client.get(f"debts/{debt_id}/payments/{payment_id}")
        return self._parse_model_response(response_data, Payment)

    def update_payment(
        self,
        debt_id: str,
        payment_id: str,
        data: Dict[str, Any],
        expand: Optional[List[str]] = None,
    ) -> Payment:
        """
        Update a payment for a debt.

        Args:
            debt_id: Debt ID
            payment_id: Payment ID
            data: Updated payment data
            expand: List of fields to expand

        Returns:
            Updated payment instance
        """
        params = self._build_expand_params(expand)
        response_data = self.http_client.patch(
            f"debts/{debt_id}/payments/{payment_id}", data=data, params=params
        )
        return self._parse_model_response(response_data, Payment)

    def list_contact_details(
        self,
        debt_id: str,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List contact details for a debt.

        Args:
            debt_id: Debt ID
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated list of contact details
        """
        params = self._build_list_params(
            limit=limit, after=after, before=before, expand=expand, **kwargs
        )
        response_data = self.http_client.get(f"debts/{debt_id}/contact-details", params=params)
        return self._parse_list_response(response_data)

    def create_contact_detail(
        self, debt_id: str, data: Dict[str, Any], expand: Optional[List[str]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create a contact detail for a debt.

        Args:
            debt_id: Debt ID
            data: Contact detail data
            expand: List of fields to expand
            **kwargs: Additional parameters

        Returns:
            Created contact detail data
        """
        params = self._build_expand_params(expand)
        params.update(kwargs)
        return self.http_client.post(f"debts/{debt_id}/contact-details", data=data, params=params)
