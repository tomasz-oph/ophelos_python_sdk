"""
Unit tests for Invoice model.
"""

from datetime import date, datetime

import pytest

from ophelos_sdk.models import Currency, Debt, Invoice, LineItem, LineItemKind


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
        assert api_body["invoiced_on"] == "2024-01-15"  # Date is serialized as ISO string
        assert api_body["due_on"] == "2024-02-15"  # Date is serialized as ISO string
        assert api_body["description"] == "Test invoice"
        assert api_body["metadata"] == {"invoice_type": "standard"}

    def test_line_item_to_api_body(self):
        """Test LineItem to_api_body method."""
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


class TestLineItemKindEnum:
    """Test cases for LineItemKind enum."""

    def test_line_item_kind_enum_values(self):
        """Test LineItemKind enum values."""
        assert LineItemKind.DEBT == "debt"
        assert LineItemKind.INTEREST == "interest"
        assert LineItemKind.FEE == "fee"
        assert LineItemKind.VAT == "vat"
        assert LineItemKind.CREDIT == "credit"
        assert LineItemKind.DISCOUNT == "discount"
        assert LineItemKind.REFUND == "refund"
        assert LineItemKind.CREDITOR_REFUND == "creditor_refund"

    def test_line_item_kind_enum_completeness(self):
        """Test that all LineItemKind enum values are defined."""
        expected_kinds = {"debt", "interest", "fee", "vat", "credit", "discount", "refund", "creditor_refund"}

        actual_kinds = {member.value for member in LineItemKind}
        assert actual_kinds == expected_kinds


class TestLineItemModel:
    """Test cases for LineItem model."""

    def test_line_item_creation_with_enum(self):
        """Test line item creation with enum values."""
        line_item = LineItem(
            kind=LineItemKind.INTEREST,
            description="Interest charge",
            amount=500,
            currency=Currency.GBP,
            transaction_at=datetime.now(),
        )

        assert line_item.kind == LineItemKind.INTEREST
        assert line_item.description == "Interest charge"
        assert line_item.amount == 500
        assert line_item.currency == Currency.GBP
        assert isinstance(line_item.transaction_at, datetime)

    def test_line_item_creation_with_string_values(self):
        """Test line item creation with string values."""
        line_item = LineItem(
            kind="fee", description="Processing fee", amount=100, currency="EUR", transaction_at=datetime.now()
        )

        assert line_item.kind == "fee"
        assert line_item.description == "Processing fee"
        assert line_item.amount == 100
        assert line_item.currency == "EUR"

    def test_line_item_minimal_creation(self):
        """Test line item creation with minimal required fields."""
        line_item = LineItem(kind=LineItemKind.DEBT, amount=10000)

        assert line_item.kind == LineItemKind.DEBT
        assert line_item.amount == 10000
        assert line_item.description is None
        assert line_item.currency is None

    def test_line_item_to_api_body_with_enums(self):
        """Test line item to_api_body with enum values."""
        line_item = LineItem(
            id="li_456",
            object="line_item",
            debt_id="debt_789",
            invoice_id="inv_123",
            kind=LineItemKind.VAT,
            description="VAT charge",
            amount=200,
            currency=Currency.USD,
            transaction_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"rate": "20%"},
        )

        api_body = line_item.to_api_body()

        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "debt_id" not in api_body
        assert "invoice_id" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # API body fields should be included
        assert api_body["kind"] == "vat"  # Enum serialized as string
        assert api_body["description"] == "VAT charge"
        assert api_body["amount"] == 200
        assert api_body["currency"] == "USD"  # Enum serialized as string
        assert api_body["metadata"] == {"rate": "20%"}

    def test_line_item_negative_amounts(self):
        """Test line item with negative amounts for credits/discounts."""
        credit_item = LineItem(
            kind=LineItemKind.CREDIT, description="Account credit", amount=-500, currency=Currency.GBP
        )

        discount_item = LineItem(
            kind=LineItemKind.DISCOUNT, description="Early payment discount", amount=-100, currency=Currency.GBP
        )

        assert credit_item.amount == -500
        assert discount_item.amount == -100

        # Test API body generation
        credit_api = credit_item.to_api_body()
        discount_api = discount_item.to_api_body()

        assert credit_api["amount"] == -500
        assert discount_api["amount"] == -100


class TestInvoiceModelEnhanced:
    """Enhanced test cases for Invoice model."""

    def test_invoice_creation_with_line_items(self):
        """Test invoice creation with LineItem objects."""
        line_item1 = LineItem(
            kind=LineItemKind.DEBT, description="Principal amount", amount=10000, currency=Currency.GBP
        )

        line_item2 = LineItem(
            kind=LineItemKind.INTEREST, description="Interest charge", amount=500, currency=Currency.GBP
        )

        invoice = Invoice(
            debt="debt_123",
            currency=Currency.GBP,
            reference="INV-2024-003",
            status="outstanding",
            line_items=[line_item1, line_item2],
            invoiced_on=date(2024, 2, 1),
            due_on=date(2024, 3, 1),
            description="Monthly invoice",
        )

        assert invoice.currency == Currency.GBP
        assert len(invoice.line_items) == 2
        assert isinstance(invoice.line_items[0], LineItem)
        assert invoice.line_items[0].kind == LineItemKind.DEBT

    def test_invoice_to_api_body_with_line_items(self):
        """Test invoice to_api_body with nested line items."""
        line_item = LineItem(
            id="li_nested", kind=LineItemKind.FEE, description="Processing fee", amount=100, currency=Currency.EUR
        )

        invoice = Invoice(
            id="inv_nested",
            debt="debt_456",
            currency=Currency.EUR,
            reference="INV-2024-004",
            status="draft",
            line_items=[line_item],
            description="Test invoice with nested items",
        )

        api_body = invoice.to_api_body()

        # debt should NOT be in API body (not in __api_body_fields__)
        assert "debt" not in api_body
        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body

        # These fields should be in the API body
        assert api_body["reference"] == "INV-2024-004"
        assert api_body["status"] == "draft"
        assert api_body["description"] == "Test invoice with nested items"

        # Line items should be processed as nested objects
        assert "line_items" in api_body
        assert len(api_body["line_items"]) == 1
        line_item_data = api_body["line_items"][0]
        assert line_item_data["kind"] == "fee"
        assert line_item_data["amount"] == 100
        assert "id" not in line_item_data  # Server fields excluded from nested items

    def test_invoice_with_currency_enum(self):
        """Test invoice creation and API body with Currency enum."""
        invoice = Invoice(currency=Currency.USD, reference="INV-USD-001", status="paid", description="USD invoice")

        assert invoice.currency == Currency.USD

        api_body = invoice.to_api_body()
        # Currency enum should be serialized as string
        assert "currency" not in api_body  # currency is not in __api_body_fields__

    def test_invoice_date_serialization_in_api_body(self):
        """Test that date fields are properly serialized in to_api_body."""
        invoice = Invoice(
            reference="INV-DATE-001",
            status="outstanding",
            invoiced_on=date(2024, 4, 1),
            due_on=date(2024, 5, 1),
            description="Date serialization test",
        )

        api_body = invoice.to_api_body()

        # Dates should be serialized as ISO format strings
        assert api_body["invoiced_on"] == "2024-04-01"
        assert api_body["due_on"] == "2024-05-01"
        assert isinstance(api_body["invoiced_on"], str)
        assert isinstance(api_body["due_on"], str)

    def test_invoice_with_debt_model(self):
        """Test invoice with expanded Debt model."""
        debt_model = Debt(id="debt_expanded", customer="cust_123", organisation="org_123")

        invoice = Invoice(debt=debt_model, reference="INV-DEBT-MODEL", status="outstanding")

        assert isinstance(invoice.debt, Debt)
        assert invoice.debt.id == "debt_expanded"

        # API body should not include debt field
        api_body = invoice.to_api_body()
        assert "debt" not in api_body
