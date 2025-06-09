"""
Pydantic models for Ophelos API data structures.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class BaseOphelosModel(BaseModel):
    """Base model for all Ophelos API resources."""

    class Config:
        extra = "allow"
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }


class DebtStatus(str, Enum):
    """Debt status enumeration."""

    PREPARED = "prepared"
    ANALYZING = "analyzing"
    CONTACTED = "contacted"
    CONTACT_ESTABLISHED = "contact_established"
    QUERIED = "queried"
    DISPUTED = "disputed"
    ADJUSTED = "adjusted"
    DEFAULTED = "defaulted"
    ASSESSING = "assessing"
    RECOVERING = "recovering"
    ARRANGING = "arranging"
    PAYING = "paying"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    LEGAL_PROTECTION = "legal_protection"
    PAID = "paid"
    SETTLED = "settled"
    CLOSED = "closed"
    WITHDRAWN = "withdrawn"
    RETURNED = "returned"
    PROCESS_EXHAUSTED = "process_exhausted"
    PAUSED = "paused"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    SCHEDULED = "scheduled"
    CANCELED = "canceled"


class ContactDetailType(str, Enum):
    """Contact detail type enumeration."""

    EMAIL = "email"
    PHONE = "phone"
    MOBILE = "mobile"
    ADDRESS = "address"


class Currency(str, Enum):
    """Currency enumeration."""

    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"


class ContactDetail(BaseOphelosModel):
    """Contact detail model."""

    id: str
    object: str = "contact_detail"
    type: ContactDetailType
    value: str
    usage: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Customer(BaseOphelosModel):
    """Customer model."""

    id: str
    object: str = "customer"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = None
    postal_code: Optional[str] = None
    preferred_locale: Optional[str] = None
    organisation_id: str
    contact_details: Optional[List[ContactDetail]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Organisation(BaseOphelosModel):
    """Organisation model."""

    id: str
    object: str = "organisation"
    name: str
    description: Optional[str] = None
    country_code: Optional[str] = None
    currency: Optional[Currency] = None
    contact_details: Optional[List[ContactDetail]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class LineItem(BaseOphelosModel):
    """Line item model."""

    id: str
    object: str = "line_item"
    kind: str
    amount: int  # Amount in cents
    description: Optional[str] = None
    transaction_at: Optional[datetime] = None
    debt_id: str
    invoice_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Invoice(BaseOphelosModel):
    """Invoice model."""

    id: str
    object: str = "invoice"
    reference: Optional[str] = None
    description: Optional[str] = None
    due_on: Optional[date] = None
    status: Optional[str] = None
    total_amount: Optional[int] = None  # Amount in cents
    remaining_amount: Optional[int] = None  # Amount in cents
    paid_amount: Optional[int] = None  # Amount in cents
    debt_id: str
    line_items: Optional[List[LineItem]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Payment(BaseOphelosModel):
    """Payment model."""

    id: str
    object: str = "payment"
    amount: int  # Amount in cents
    currency: Optional[Currency] = None
    status: PaymentStatus
    payment_provider: Optional[str] = None
    transaction_ref: Optional[str] = None
    transaction_at: datetime
    debt_id: str
    organisation_id: str
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class PaymentPlan(BaseOphelosModel):
    """Payment plan model."""

    id: str
    object: str = "payment_plan"
    status: str
    amount: int  # Amount in cents
    currency: Optional[Currency] = None
    frequency: str
    installments: int
    next_payment_on: Optional[date] = None
    start_on: Optional[date] = None
    activated_at: Optional[datetime] = None
    debt_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Debt(BaseOphelosModel):
    """Debt model."""

    id: str
    object: str = "debt"
    account_number: Optional[str] = None
    reference_code: Optional[str] = None
    total_amount: int  # Amount in cents
    currency: Optional[Currency] = None
    status: DebtStatus
    kind: Optional[str] = None
    start_at: Optional[date] = None
    suspended_at: Optional[datetime] = None
    suspended_until: Optional[datetime] = None
    customer_id: str
    organisation_id: str
    customer: Optional[Customer] = None
    organisation: Optional[Organisation] = None
    line_items: Optional[List[LineItem]] = None
    payments: Optional[List[Payment]] = None
    invoices: Optional[List[Invoice]] = None
    payment_plans: Optional[List[PaymentPlan]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Communication(BaseOphelosModel):
    """Communication model."""

    id: str
    object: str = "communication"
    type: str
    status: str
    direction: str
    channel: str
    subject: Optional[str] = None
    content: Optional[str] = None
    debt_id: str
    customer_id: str
    organisation_id: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Webhook(BaseOphelosModel):
    """Webhook model."""

    id: str
    object: str = "webhook"
    url: str
    events: List[str]
    status: str
    secret: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class WebhookEvent(BaseOphelosModel):
    """Webhook event model."""

    id: str
    object: str = "event"
    type: str
    data: Dict[str, Any]
    created_at: datetime
    livemode: bool = False


class PaginatedResponse(BaseOphelosModel):
    """Paginated response model."""

    object: str = "list"
    data: List[Union[Dict[str, Any], BaseOphelosModel]]
    has_more: bool = False
    total_count: Optional[int] = None


class Tenant(BaseOphelosModel):
    """Tenant model."""

    id: str
    object: str = "tenant"
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Payout(BaseOphelosModel):
    """Payout model."""

    id: str
    object: str = "payout"
    amount: int  # Amount in cents
    currency: Optional[Currency] = None
    status: str
    payout_date: Optional[date] = None
    organisation_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
