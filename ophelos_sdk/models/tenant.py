"""
Tenant-related models for Ophelos SDK.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from .base import BaseOphelosModel


class Tenant(BaseOphelosModel):
    """Tenant model."""

    id: str
    object: str = "tenant"
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
