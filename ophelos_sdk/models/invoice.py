from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
from enum import Enum

from .base import BaseOphelosModel, Currency

if TYPE_CHECKING:
    from .debt import Debt


class LineItemKind(str, Enum):
    """Line item kind enumeration."""

    DEBT = "debt"
    INTEREST = "interest"
    FEE = "fee"
    VAT = "vat"
    CREDIT = "credit"  # Amount must be negative
    DISCOUNT = "discount"  # Amount must be negative
    REFUND = "refund"
    CREDITOR_REFUND = "creditor_refund"


class LineItem(BaseOphelosModel):
    """Line item model."""

    id: str
    object: str = "line_item"
    debt_id: str
    invoice_id: Optional[str] = None
    kind: LineItemKind
    description: Optional[str] = None
    amount: int
    currency: Optional[Currency] = None
    transaction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "description",
        "kind",
        "amount",
        "currency",
        "transaction_at",
        "metadata",
    }


class Invoice(BaseOphelosModel):
    """Invoice model."""

    id: str
    object: str = "invoice"
    debt: Union[str, "Debt"]  # Can be debt ID or expanded debt object
    currency: Optional[Currency] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    invoiced_on: Optional[date] = None
    due_on: Optional[date] = None
    description: Optional[str] = None
    line_items: Optional[List[Union[str, LineItem]]] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "description",
        "reference",
        "status",
        "invoiced_on",
        "due_on",
        "line_items",
        "metadata",
    }
