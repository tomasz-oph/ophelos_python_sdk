from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
from enum import Enum

from .base import BaseOphelosModel

if TYPE_CHECKING:
    from .debt import Debt


class ContactDetailType(str, Enum):
    """Contact detail type enumeration."""

    EMAIL = "email"
    PHONE = "phone"
    MOBILE = "mobile"
    ADDRESS = "address"


class ContactDetail(BaseOphelosModel):
    """Contact detail model."""

    id: str
    object: str = "contact_detail"
    type: ContactDetailType
    value: str
    primary: Optional[bool] = None
    usage: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {"type", "value", "primary", "usage", "source", "status", "metadata"}


class Customer(BaseOphelosModel):
    """Customer model."""

    id: str
    object: str = "customer"
    kind: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_locale: Optional[str] = None
    date_of_birth: Optional[date] = None
    contact_details: Optional[List[Union[str, ContactDetail]]] = None  # Can be IDs or objects
    debts: Optional[List[Union[str, "Debt"]]] = None  # Can be IDs or objects
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    # Define which fields can be sent in API create/update requests
    __api_body_fields__ = {
        "kind",
        "full_name",
        "first_name",
        "last_name",
        "preferred_locale",
        "date_of_birth",
        "contact_details",
        "metadata",
    }
