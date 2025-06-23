"""
Pagination-related models for Ophelos SDK.
"""

from typing import Optional, List, Union, Dict, Any

from .base import BaseOphelosModel


class PaginatedResponse(BaseOphelosModel):
    """Paginated response model."""

    object: str = "list"
    data: List[Union[Dict[str, Any], BaseOphelosModel]]
    has_more: bool = False
    total_count: Optional[int] = None
