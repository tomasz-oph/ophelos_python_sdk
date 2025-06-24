"""
Unit tests for Webhook model.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from ophelos_sdk.models import Webhook


class TestWebhook:
    """Test cases for Webhook model."""

    def test_webhook_creation_minimal(self):
        """Test webhook creation with minimal required fields."""
        webhook = Webhook(url="https://example.com/webhook")
        
        assert webhook.id is None
        assert webhook.object == "webhook"
        assert webhook.url == "https://example.com/webhook"
        assert webhook.enabled is None
        assert webhook.signing_key is None
        assert webhook.enabled_events is None
        assert webhook.version is None
        assert webhook.metadata is None
        assert webhook.created_at is None
        assert webhook.updated_at is None

    def test_webhook_creation_with_all_fields(self):
        """Test webhook creation with all fields."""
        events = ["customer.created", "debt.updated", "payment.completed"]
        created_time = datetime.now()
        updated_time = datetime.now()
        
        webhook = Webhook(
            id="webhook_123",
            object="webhook",
            url="https://api.example.com/webhooks/ophelos",
            enabled=True,
            signing_key="whsec_test_secret_key_123",
            enabled_events=events,
            version="v1",
            metadata={
                "environment": "production",
                "team": "backend",
                "priority": "high"
            },
            created_at=created_time,
            updated_at=updated_time
        )
        
        assert webhook.id == "webhook_123"
        assert webhook.object == "webhook"
        assert webhook.url == "https://api.example.com/webhooks/ophelos"
        assert webhook.enabled is True
        assert webhook.signing_key == "whsec_test_secret_key_123"
        assert webhook.enabled_events == events
        assert webhook.version == "v1"
        assert webhook.metadata == {
            "environment": "production",
            "team": "backend",
            "priority": "high"
        }
        assert webhook.created_at == created_time
        assert webhook.updated_at == updated_time

    def test_webhook_with_single_event(self):
        """Test webhook creation with single event."""
        webhook = Webhook(
            url="https://example.com/single-event",
            enabled_events=["payment.completed"],
            enabled=True
        )
        
        assert webhook.url == "https://example.com/single-event"
        assert webhook.enabled_events == ["payment.completed"]
        assert webhook.enabled is True

    def test_webhook_with_multiple_events(self):
        """Test webhook creation with multiple events."""
        events = [
            "customer.created",
            "customer.updated",
            "debt.created",
            "debt.updated",
            "debt.status_changed",
            "payment.created",
            "payment.completed",
            "payment.failed",
            "invoice.created",
            "invoice.sent"
        ]
        
        webhook = Webhook(
            url="https://example.com/all-events",
            enabled_events=events,
            enabled=True
        )
        
        assert webhook.enabled_events == events
        assert len(webhook.enabled_events) == 10

    def test_webhook_to_api_body_basic(self):
        """Test webhook to_api_body with basic fields."""
        webhook = Webhook(
            id="webhook_api_test",
            object="webhook",
            url="https://api.test.com/webhook",
            enabled=True,
            enabled_events=["customer.created", "debt.updated"],
            signing_key="whsec_api_test_secret",
            version="v1",
            metadata={"test": True, "version": "v1"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        api_body = webhook.to_api_body()
        
        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body
        
        # Client fields should be included
        assert api_body["url"] == "https://api.test.com/webhook"
        assert api_body["enabled"] is True
        assert api_body["enabled_events"] == ["customer.created", "debt.updated"]
        assert api_body["signing_key"] == "whsec_api_test_secret"
        assert api_body["version"] == "v1"
        assert api_body["metadata"] == {"test": True, "version": "v1"}

    def test_webhook_to_api_body_exclude_none_false(self):
        """Test webhook to_api_body includes None values when exclude_none=False."""
        webhook = Webhook(
            url="https://include-none.example.com/webhook",
            enabled=None,
            enabled_events=None,
            signing_key=None,
            version=None,
            metadata=None
        )
        
        api_body = webhook.to_api_body(exclude_none=False)
        
        assert api_body["url"] == "https://include-none.example.com/webhook"
        # None values should be included
        assert "enabled" in api_body
        assert api_body["enabled"] is None
        assert "enabled_events" in api_body
        assert api_body["enabled_events"] is None
        assert "signing_key" in api_body
        assert api_body["signing_key"] is None
        assert "version" in api_body
        assert api_body["version"] is None
        assert "metadata" in api_body
        assert api_body["metadata"] is None

    def test_webhook_url_formats(self):
        """Test webhook with different URL formats."""
        url_cases = [
            "https://example.com/webhook",
            "https://api.example.com/v1/webhooks/ophelos",
            "https://subdomain.example.com/path/to/webhook",
            "https://example.com:8080/webhook",
            "https://example.com/webhook?param=value",
            "https://webhook-service.internal/receive"
        ]
        
        for url in url_cases:
            webhook = Webhook(url=url)
            
            assert webhook.url == url
            
            api_body = webhook.to_api_body()
            assert api_body["url"] == url

    def test_webhook_signing_key_formats(self):
        """Test webhook with different signing key formats."""
        signing_key_cases = [
            "whsec_simple_secret",
            "whsec_1234567890abcdef",
            "sk_test_webhook_secret_key",
            "webhook_secret_with_underscores",
            "webhook-secret-with-hyphens",
            "VeryLongWebhookSecretKeyThatMightBeUsedInProduction123"
        ]
        
        for signing_key in signing_key_cases:
            webhook = Webhook(
                url="https://example.com/webhook",
                signing_key=signing_key
            )
            
            assert webhook.signing_key == signing_key
            
            api_body = webhook.to_api_body()
            assert api_body["signing_key"] == signing_key

    def test_webhook_event_types(self):
        """Test webhook with various event types."""
        event_categories = {
            "customer": [
                "customer.created",
                "customer.updated",
                "customer.deleted"
            ],
            "debt": [
                "debt.created",
                "debt.updated",
                "debt.status_changed",
                "debt.deleted"
            ],
            "payment": [
                "payment.created",
                "payment.completed",
                "payment.failed",
                "payment.cancelled"
            ],
            "invoice": [
                "invoice.created",
                "invoice.sent",
                "invoice.paid",
                "invoice.overdue"
            ]
        }
        
        for category, events in event_categories.items():
            webhook = Webhook(
                url=f"https://example.com/{category}-webhook",
                enabled_events=events,
                enabled=True
            )
            
            assert webhook.enabled_events == events
            assert webhook.enabled is True
            
            api_body = webhook.to_api_body()
            assert api_body["enabled_events"] == events

    def test_webhook_complex_metadata(self):
        """Test webhook with complex metadata."""
        complex_metadata = {
            "configuration": {
                "retry_policy": {
                    "max_retries": 3,
                    "backoff_multiplier": 2,
                    "initial_delay_seconds": 1
                },
                "timeout_seconds": 30,
                "verify_ssl": True
            },
            "tags": ["production", "critical", "customer-facing"],
            "team_contact": {
                "email": "webhooks@example.com",
                "slack_channel": "#webhook-alerts"
            },
            "monitoring": {
                "enabled": True,
                "alert_on_failure": True,
                "success_rate_threshold": 0.95
            }
        }
        
        webhook = Webhook(
            url="https://example.com/complex-webhook",
            enabled_events=["customer.created", "payment.completed"],
            enabled=True,
            metadata=complex_metadata
        )
        
        assert webhook.metadata == complex_metadata
        assert webhook.metadata["configuration"]["retry_policy"]["max_retries"] == 3
        assert webhook.metadata["monitoring"]["enabled"] is True
        
        api_body = webhook.to_api_body()
        assert api_body["metadata"] == complex_metadata

    def test_webhook_empty_events_list(self):
        """Test webhook with empty events list."""
        webhook = Webhook(
            url="https://example.com/no-events",
            enabled_events=[],
            enabled=False
        )
        
        assert webhook.enabled_events == []
        assert webhook.enabled is False
        
        api_body = webhook.to_api_body()
        assert api_body["enabled_events"] == []
        assert api_body["enabled"] is False

    def test_webhook_version_values(self):
        """Test webhook with different version values."""
        version_cases = ["v1", "v2", "latest", "2023-01-01", "1.0.0"]
        
        for version in version_cases:
            webhook = Webhook(
                url="https://example.com/versioned-webhook",
                version=version,
                enabled=True
            )
            
            assert webhook.version == version
            
            api_body = webhook.to_api_body()
            assert api_body["version"] == version

    def test_webhook_enabled_states(self):
        """Test webhook with different enabled states."""
        enabled_cases = [True, False]
        
        for enabled in enabled_cases:
            webhook = Webhook(
                url="https://example.com/enabled-test",
                enabled=enabled,
                enabled_events=["test.event"]
            )
            
            assert webhook.enabled is enabled
            
            api_body = webhook.to_api_body()
            assert api_body["enabled"] is enabled
