"""
Unit tests for Invoice model.
"""

import pytest
from datetime import datetime, date

from ophelos_sdk.models import Invoice, Debt, Currency


class TestUpdatedInvoiceModel:
    """Test cases for updated Invoice model."""

    def test_invoice_with_expandable_debt(self):
        """Test invoice with expandable debt field."""
        invoice_data = {
            "id": "inv_123",
            "object": "invoice",
            "debt": {
                "id": "debt_456",
                "object": "debt",
                "status": {
                    "value": "prepared",
                    "whodunnit": "system",
                    "context": None,
                    "reason": None,
                    "updated_at": datetime.now().isoformat(),
                },
                "customer": "cust_789",
                "organisation": "org_101",
                "summary": {"amount_total": 5000, "amount_paid": 0, "amount_remaining": 5000},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            "currency": "GBP",
            "reference": "INV-2024-001",
            "status": "outstanding",
            "invoiced_on": "2024-01-15",
            "due_on": "2024-02-15",
            "description": "Test invoice",
            "line_items": ["li_123", "li_456"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {"invoice_type": "standard"},
        }

        invoice = Invoice(**invoice_data)

        assert invoice.id == "inv_123"
        assert invoice.object == "invoice"
        assert isinstance(invoice.debt, Debt)  # Expanded debt object
        assert invoice.debt.id == "debt_456"
        assert invoice.currency == Currency.GBP
        assert invoice.reference == "INV-2024-001"
        assert invoice.status == "outstanding"
        assert invoice.invoiced_on == date(2024, 1, 15)
        assert invoice.due_on == date(2024, 2, 15)
        assert invoice.description == "Test invoice"
        assert invoice.line_items == ["li_123", "li_456"]
        assert invoice.metadata == {"invoice_type": "standard"}

    def test_invoice_with_debt_id(self):
        """Test invoice with debt as string ID."""
        invoice_data = {
            "id": "inv_789",
            "object": "invoice",
            "debt": "debt_456",
            "currency": "EUR",
            "reference": "INV-2024-002",
            "status": "paid",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        invoice = Invoice(**invoice_data)

        assert invoice.id == "inv_789"
        assert invoice.debt == "debt_456"  # String debt ID
        assert invoice.currency == Currency.EUR
        assert invoice.reference == "INV-2024-002"
        assert invoice.status == "paid"
        assert invoice.invoiced_on is None
        assert invoice.due_on is None
        assert invoice.description is None
        assert invoice.line_items is None
        assert invoice.metadata is None 