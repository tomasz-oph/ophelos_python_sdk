"""
Payout-related models for Ophelos SDK.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any

from .base import BaseOphelosModel, Currency


class Payout(BaseOphelosModel):
    """Payout model."""

    id: Optional[str] = None
    object: Optional[str] = "payout"
    amount: int  # Amount in cents
    currency: Optional[Currency] = None
    status: Optional[str] = None
    payout_date: Optional[date] = None
    organisation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
