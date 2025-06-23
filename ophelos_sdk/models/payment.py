from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
from enum import Enum

from .base import BaseOphelosModel, Currency

if TYPE_CHECKING:
    from .debt import Debt


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    SCHEDULED = "scheduled"
    CANCELED = "canceled"


class Payment(BaseOphelosModel):
    """Payment model."""

    id: str
    object: str = "payment"
    debt: Union[str, "Debt"]  # Can be debt ID or expanded debt object
    status: PaymentStatus
    transaction_at: datetime
    transaction_ref: Optional[str] = None
    amount: int  # Amount in cents (amount_in_cents from jbuilder)
    currency: Optional[Currency] = None  # amount_currency from jbuilder
    payment_provider: Optional[str] = None  # underscore.downcase from jbuilder
    payment_plan: Optional[Union[str, "PaymentPlan"]] = None  # Can be payment_plan ID or expanded object
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {"transaction_at", "transaction_ref", "amount", "currency", "metadata"}


class PaymentPlan(BaseOphelosModel):
    """Payment plan model."""

    id: str
    object: str = "payment_plan"
    debt: Union[str, "Debt"]  # Can be debt ID or expanded debt object (from jbuilder)
    status: str  # From item.status in jbuilder
    schedule: Optional[List[Union[str, Any]]] = None  # Can be schedule IDs or expanded objects (from jbuilder)
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
