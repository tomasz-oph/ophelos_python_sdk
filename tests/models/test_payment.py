"""
Unit tests for Payment model.
"""

from datetime import datetime

from ophelos_sdk.models import Currency, Debt, Payment, PaymentPlan, PaymentStatus


class TestPaymentModel:
    """Test cases for Payment model."""

    def test_payment_creation(self, sample_payment_data):
        """Test payment model creation with valid data."""
        payment = Payment(**sample_payment_data)

        assert payment.id == sample_payment_data["id"]
        assert payment.amount == sample_payment_data["amount"]
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.debt == sample_payment_data["debt"]

    def test_payment_status_enum(self):
        """Test payment status enumeration."""
        assert PaymentStatus.SUCCEEDED == "succeeded"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.DISPUTED == "disputed"

    def test_payment_to_api_body(self):
        """Test payment to_api_body method."""
        payment = Payment(
            id="pay_123",
            object="payment",
            debt="debt_123",
            status=PaymentStatus.SUCCEEDED,
            transaction_at=datetime.now(),
            transaction_ref="TXN-123",
            amount=10000,
            currency="GBP",
            payment_provider="stripe",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"gateway_id": "pi_123"},
        )

        api_body = payment.to_api_body()

        # debt should NOT be in API body as it's set by endpoint context
        assert "debt" not in api_body
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body

        # These fields should be in the API body (based on __api_body_fields__)
        assert api_body["transaction_ref"] == "TXN-123"
        assert api_body["amount"] == 10000
        assert api_body["currency"] == "GBP"
        assert api_body["metadata"] == {"gateway_id": "pi_123"}

        # These fields are NOT in __api_body_fields__ so should be excluded
        assert "status" not in api_body
        assert "payment_provider" not in api_body
        assert "payment_plan" not in api_body

    def test_payment_creation_with_optional_fields(self):
        """Test payment creation with all fields optional."""
        # Should be able to create with no fields
        payment_empty = Payment()
        assert payment_empty.id is None
        assert payment_empty.transaction_at is None
        assert payment_empty.transaction_ref is None
        assert payment_empty.amount is None
        assert payment_empty.currency is None
        assert payment_empty.metadata is None

        # Should be able to create with only some fields
        payment_partial = Payment(metadata={"source": "test"}, transaction_ref="PARTIAL-REF")
        assert payment_partial.metadata == {"source": "test"}
        assert payment_partial.transaction_ref == "PARTIAL-REF"
        assert payment_partial.amount is None
        assert payment_partial.currency is None

    def test_payment_partial_update_metadata_only(self):
        """Test payment model for metadata-only updates."""
        payment = Payment(metadata={"status": "verified", "notes": "Updated"})

        api_body = payment.to_api_body()

        # Should only contain metadata
        assert "metadata" in api_body
        assert api_body["metadata"] == {"status": "verified", "notes": "Updated"}

        # Should not contain other fields
        assert "transaction_at" not in api_body
        assert "transaction_ref" not in api_body
        assert "amount" not in api_body
        assert "currency" not in api_body

    def test_payment_partial_update_transaction_ref_only(self):
        """Test payment model for transaction_ref-only updates."""
        payment = Payment(transaction_ref="UPDATED-REF-123")

        api_body = payment.to_api_body()

        # Should only contain transaction_ref
        assert "transaction_ref" in api_body
        assert api_body["transaction_ref"] == "UPDATED-REF-123"

        # Should not contain other fields
        assert "metadata" not in api_body
        assert "transaction_at" not in api_body
        assert "amount" not in api_body
        assert "currency" not in api_body

    def test_payment_partial_update_multiple_fields(self):
        """Test payment model for partial updates with multiple fields."""
        payment = Payment(transaction_ref="MULTI-REF-456", amount=15000, metadata={"source": "partial_update"})

        api_body = payment.to_api_body()

        # Should contain provided fields
        assert api_body["transaction_ref"] == "MULTI-REF-456"
        assert api_body["amount"] == 15000
        assert api_body["metadata"] == {"source": "partial_update"}

        # Should not contain unprovided fields
        assert "transaction_at" not in api_body
        assert "currency" not in api_body

    def test_payment_empty_api_body(self):
        """Test payment model with no fields set produces empty API body."""
        payment = Payment()

        api_body = payment.to_api_body()

        # Should be empty
        assert api_body == {}

    def test_payment_api_body_excludes_none_values(self):
        """Test that to_api_body() excludes None values."""
        payment = Payment(
            transaction_ref="TEST-REF",
            amount=None,  # Explicitly set to None
            currency=Currency.GBP,
            metadata=None,  # Explicitly set to None
        )

        api_body = payment.to_api_body()

        # Should include non-None fields
        assert api_body["transaction_ref"] == "TEST-REF"
        assert api_body["currency"] == "GBP"

        # Should exclude None fields
        assert "amount" not in api_body
        assert "metadata" not in api_body
        assert "transaction_at" not in api_body


class TestPaymentStatusEnum:
    """Test cases for PaymentStatus enum."""

    def test_payment_status_enum_completeness(self):
        """Test that all payment status enum values are defined."""
        expected_statuses = {"pending", "succeeded", "failed", "disputed", "refunded", "scheduled", "canceled"}

        actual_statuses = {member.value for member in PaymentStatus}
        assert actual_statuses == expected_statuses

    def test_payment_status_specific_values(self):
        """Test specific payment status enum values."""
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.SUCCEEDED == "succeeded"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.DISPUTED == "disputed"
        assert PaymentStatus.REFUNDED == "refunded"
        assert PaymentStatus.SCHEDULED == "scheduled"
        assert PaymentStatus.CANCELED == "canceled"


class TestPaymentModelEnhanced:
    """Enhanced test cases for Payment model."""

    def test_payment_creation_with_enums(self):
        """Test payment creation with enum values."""
        payment = Payment(
            id="pay_enum_test",
            status=PaymentStatus.SUCCEEDED,
            transaction_at=datetime.now(),
            transaction_ref="TXN-ENUM-001",
            amount=15000,
            currency=Currency.EUR,
            payment_provider="paypal",
        )

        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.currency == Currency.EUR
        assert payment.amount == 15000
        assert payment.transaction_ref == "TXN-ENUM-001"

    def test_payment_with_debt_model(self):
        """Test payment with expanded Debt model."""
        debt_model = Debt(id="debt_payment_test", customer="cust_123", organisation="org_123")

        payment = Payment(
            id="pay_debt_model",
            debt=debt_model,
            status=PaymentStatus.PENDING,
            transaction_at=datetime.now(),
            transaction_ref="TXN-DEBT-001",
            amount=8000,
            currency=Currency.GBP,
        )

        assert isinstance(payment.debt, Debt)
        assert payment.debt.id == "debt_payment_test"

        # API body should not include debt field
        api_body = payment.to_api_body()
        assert "debt" not in api_body

    def test_payment_with_payment_plan_model(self):
        """Test payment with PaymentPlan model."""
        payment_plan = PaymentPlan(id="pp_123", status="active")

        payment = Payment(
            id="pay_plan_test",
            debt="debt_456",
            payment_plan=payment_plan,
            status=PaymentStatus.SCHEDULED,
            transaction_at=datetime.now(),
            transaction_ref="TXN-PLAN-001",
            amount=2500,
            currency=Currency.USD,
        )

        assert isinstance(payment.payment_plan, PaymentPlan)
        assert payment.payment_plan.id == "pp_123"
        assert payment.status == PaymentStatus.SCHEDULED

    def test_payment_to_api_body_with_currency_enum(self):
        """Test payment to_api_body with Currency enum."""
        payment = Payment(
            id="pay_currency_test",
            status=PaymentStatus.SUCCEEDED,
            transaction_at=datetime.now(),
            transaction_ref="TXN-CURRENCY-001",
            amount=12000,
            currency=Currency.USD,
            metadata={"processor": "stripe", "fee": 300},
        )

        api_body = payment.to_api_body()

        assert api_body["transaction_ref"] == "TXN-CURRENCY-001"
        assert api_body["amount"] == 12000
        assert api_body["currency"] == "USD"  # Enum serialized as string
        assert api_body["metadata"] == {"processor": "stripe", "fee": 300}

        # Fields not in __api_body_fields__ should be excluded
        assert "status" not in api_body
        assert "payment_provider" not in api_body
        assert "payment_plan" not in api_body

    def test_payment_datetime_serialization_in_api_body(self):
        """Test that datetime fields are properly serialized in to_api_body."""
        transaction_time = datetime(2024, 3, 15, 14, 30, 0)

        payment = Payment(
            id="pay_datetime_test",
            transaction_at=transaction_time,
            transaction_ref="TXN-DATETIME-001",
            amount=5500,
            currency=Currency.EUR,
        )

        api_body = payment.to_api_body()

        # Datetime should be serialized as ISO format string
        assert isinstance(api_body["transaction_at"], str)
        assert "2024-03-15T14:30:00" in api_body["transaction_at"]

    def test_payment_full_create_vs_partial_update_scenarios(self):
        """Test the difference between full create and partial update scenarios."""
        # Full create scenario
        payment_create = Payment(
            transaction_at=datetime(2023, 12, 1, 10, 30, 0),
            transaction_ref="CREATE-REF-789",
            amount=20000,
            currency=Currency.GBP,
            metadata={"source": "create_operation"},
        )

        create_body = payment_create.to_api_body()

        # Should contain all provided fields
        assert "transaction_at" in create_body
        assert "transaction_ref" in create_body
        assert "amount" in create_body
        assert "currency" in create_body
        assert "metadata" in create_body

        # Partial update scenario
        payment_update = Payment(metadata={"source": "update_operation"})

        update_body = payment_update.to_api_body()

        # Should only contain metadata
        assert "metadata" in update_body
        assert len(update_body) == 1
        assert update_body["metadata"] == {"source": "update_operation"}


class TestPaymentPlan:
    """Test cases for PaymentPlan model."""

    def test_payment_plan_creation_minimal(self):
        """Test payment plan creation with minimal fields."""
        plan = PaymentPlan()

        assert plan.id is None
        assert plan.object == "payment_plan"
        assert plan.debt is None
        assert plan.status is None
        assert plan.schedule is None
        assert plan.created_at is None
        assert plan.updated_at is None
        assert plan.metadata is None

    def test_payment_plan_creation_with_fields(self):
        """Test payment plan creation with fields."""
        plan = PaymentPlan(
            id="pp_456",
            debt="debt_789",
            status="active",
            schedule=["schedule_1", "schedule_2"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"type": "installment", "frequency": "monthly"},
        )

        assert plan.id == "pp_456"
        assert plan.debt == "debt_789"
        assert plan.status == "active"
        assert plan.schedule == ["schedule_1", "schedule_2"]
        assert plan.metadata == {"type": "installment", "frequency": "monthly"}

    def test_payment_plan_with_debt_model(self):
        """Test payment plan with expanded Debt model."""
        debt_model = Debt(id="debt_plan_test", customer="cust_456", organisation="org_456")

        plan = PaymentPlan(
            id="pp_debt_model", debt=debt_model, status="pending", created_at=datetime.now(), updated_at=datetime.now()
        )

        assert isinstance(plan.debt, Debt)
        assert plan.debt.id == "debt_plan_test"
        assert plan.status == "pending"
