"""
Unit tests for enumeration types.
"""

import pytest

from ophelos_sdk.models import Currency, ContactDetailType


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
        assert ContactDetailType.PHONE_NUMBER == "phone_number"
        assert ContactDetailType.MOBILE_NUMBER == "mobile_number"
        assert ContactDetailType.FAX_NUMBER == "fax_number"
        assert ContactDetailType.ADDRESS == "address"
