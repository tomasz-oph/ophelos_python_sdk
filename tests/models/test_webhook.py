"""
Unit tests for webhook event model.
"""

import pytest
from datetime import datetime

from ophelos_sdk.models import WebhookEvent


class TestWebhookEvent:
    """Test cases for webhook event model."""

    def test_webhook_event_creation(self, sample_webhook_event):
        """Test webhook event creation."""
        event = WebhookEvent(**sample_webhook_event)

        assert event.id == sample_webhook_event["id"]
        assert event.type == sample_webhook_event["type"]
        assert event.data == sample_webhook_event["data"]
        assert event.livemode is False

    def test_webhook_event_types(self):
        """Test common webhook event types."""
        event_types = [
            "debt.created",
            "debt.updated",
            "debt.closed",
            "payment.succeeded",
            "payment.failed",
            "customer.created",
        ]

        for event_type in event_types:
            event_data = {
                "id": "evt_123",
                "object": "event",
                "type": event_type,
                "created_at": datetime.now().isoformat(),
                "livemode": False,
                "data": {"test": "data"},
            }

            event = WebhookEvent(**event_data)
            assert event.type == event_type 