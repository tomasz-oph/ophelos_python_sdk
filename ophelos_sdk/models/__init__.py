"""
Ophelos SDK Models Package

This package contains all Pydantic models for Ophelos API data structures.
Models are organized by domain for better maintainability.
"""

# Import all models for backward compatibility
from .base import BaseOphelosModel, Currency
from .customer import Customer, ContactDetail, ContactDetailType, ContactDetailUsage, ContactDetailSource
from .debt import Debt, DebtStatus, StatusObject, DebtSummary, SummaryBreakdown
from .payment import Payment, PaymentPlan, PaymentStatus
from .invoice import Invoice, LineItem, LineItemKind
from .communication import Communication, CommunicationTemplate
from .webhook import Webhook, WebhookEvent
from .organisation import Organisation, PaymentOptionsConfiguration
from .tenant import Tenant
from .payout import Payout
from .pagination import PaginatedResponse

# Rebuild models to resolve forward references
Customer.model_rebuild()
Debt.model_rebuild()
Payment.model_rebuild()
PaymentPlan.model_rebuild()
Invoice.model_rebuild()
Communication.model_rebuild()
Organisation.model_rebuild()

# Export all models
__all__ = [
    # Base
    "BaseOphelosModel",
    "Currency",
    # Customer
    "Customer",
    "ContactDetail",
    "ContactDetailType",
    "ContactDetailUsage",
    "ContactDetailSource",
    # Debt
    "Debt",
    "DebtStatus",
    "StatusObject",
    "DebtSummary",
    "SummaryBreakdown",
    # Payment
    "Payment",
    "PaymentPlan",
    "PaymentStatus",
    # Invoice
    "Invoice",
    "LineItem",
    "LineItemKind",
    # Communication
    "Communication",
    "CommunicationTemplate",
    # Webhook
    "Webhook",
    "WebhookEvent",
    # Organisation
    "Organisation",
    "PaymentOptionsConfiguration",
    # Tenant
    "Tenant",
    # Payout
    "Payout",
    # Pagination
    "PaginatedResponse",
]
