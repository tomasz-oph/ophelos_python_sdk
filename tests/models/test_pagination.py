"""
Unit tests for paginated response model.
"""

from ophelos_sdk.models import PaginatedResponse


class TestPaginatedResponse:
    """Test cases for paginated response model."""

    def test_empty_paginated_response(self):
        """Test empty paginated response."""
        response = PaginatedResponse(data=[])

        assert response.object == "list"
        assert response.data == []
        assert response.has_more is False
        assert response.total_count is None

    def test_paginated_response_with_data(self, sample_debt_data):
        """Test paginated response with data."""
        response_data = {
            "object": "list",
            "data": [sample_debt_data],
            "has_more": True,
            "total_count": 10,
        }

        response = PaginatedResponse(**response_data)
        assert len(response.data) == 1
        assert response.has_more is True
        assert response.total_count == 10
        assert response.pagination is None

    def test_paginated_response_with_pagination_info(self, sample_debt_data):
        """Test paginated response with pagination cursor information."""
        pagination_info = {
            "next": {"after": "deb_123", "limit": 10, "url": "https://api.ophelos.com/debts?after=deb_123&limit=10"},
            "prev": {"before": "deb_456", "limit": 10, "url": "https://api.ophelos.com/debts?before=deb_456&limit=10"},
        }

        response_data = {
            "object": "list",
            "data": [sample_debt_data],
            "has_more": True,
            "total_count": 25,
            "pagination": pagination_info,
        }

        response = PaginatedResponse(**response_data)
        assert len(response.data) == 1
        assert response.has_more is True
        assert response.total_count == 25
        assert response.pagination is not None
        assert "next" in response.pagination
        assert "prev" in response.pagination
        assert response.pagination["next"]["after"] == "deb_123"
        assert response.pagination["prev"]["before"] == "deb_456"
