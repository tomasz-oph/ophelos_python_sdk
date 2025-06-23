"""
Payout-related models for Ophelos SDK.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any

from .base import BaseOphelosModel, Currency


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
