"""
Unit tests for enumeration types.
"""

import pytest

from ophelos.models import Currency, ContactDetailType


class TestEnumerations:
    """Test cases for enumeration types."""

    def test_currency_enum(self):
        """Test currency enumeration."""
        assert Currency.GBP == "GBP"
        assert Currency.EUR == "EUR"
        assert Currency.USD == "USD"

    def test_contact_detail_type_enum(self):
        """Test contact detail type enumeration."""
        assert ContactDetailType.EMAIL == "email"
        assert ContactDetailType.PHONE == "phone"
        assert ContactDetailType.MOBILE == "mobile"
        assert ContactDetailType.ADDRESS == "address" 