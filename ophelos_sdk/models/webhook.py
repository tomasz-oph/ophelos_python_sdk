"""
Webhook-related models for Ophelos SDK.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from .base import BaseOphelosModel


class Webhook(BaseOphelosModel):
    """Webhook model."""

    id: str
    object: str = "webhook"
    url: str  # From item.endpoint in jbuilder
    enabled: bool  # From item.enabled in jbuilder
    signing_key: Optional[str] = None  # From item.signing_key in jbuilder
    enabled_events: List[str]  # From item.enabled_events in jbuilder
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class WebhookEvent(BaseOphelosModel):
    """Webhook event model."""

    id: str
    object: str = "event"
    type: str
    data: Dict[str, Any]
    created_at: datetime
    livemode: bool = False
