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

    def test_invoice_to_api_body(self):
        """Test invoice to_api_body method."""
        invoice = Invoice(
            id="inv_123",
            object="invoice",
            debt="debt_456",
            currency="GBP",
            reference="INV-2024-001",
            status="outstanding",
            invoiced_on=date(2024, 1, 15),
            due_on=date(2024, 2, 15),
            description="Test invoice",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"invoice_type": "standard"},
        )

        api_body = invoice.to_api_body()

        # debt should NOT be in API body (not in __api_body_fields__)
        assert "debt" not in api_body
        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # These fields should be in the API body
        assert api_body["reference"] == "INV-2024-001"
        assert api_body["status"] == "outstanding"
        assert api_body["invoiced_on"] == date(2024, 1, 15)
        assert api_body["due_on"] == date(2024, 2, 15)
        assert api_body["description"] == "Test invoice"
        assert api_body["metadata"] == {"invoice_type": "standard"}

    def test_line_item_to_api_body(self):
        """Test LineItem to_api_body method."""
        from ophelos_sdk.models import LineItem

        line_item = LineItem(
            id="li_123",
            object="line_item",
            debt_id="debt_456",
            kind="debt",  # Using valid enum value
            description="Debt amount",
            amount=5000,
            currency="GBP",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "debt"},
        )

        api_body = line_item.to_api_body()

        # debt_id should NOT be in API body (not in __api_body_fields__)
        assert "debt_id" not in api_body
        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # These fields should be in the API body
        assert api_body["kind"] == "debt"
        assert api_body["description"] == "Debt amount"
        assert api_body["amount"] == 5000
        assert api_body["currency"] == "GBP"
        assert api_body["metadata"] == {"category": "debt"}
