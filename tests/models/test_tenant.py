"""
Unit tests for Tenant model.
"""

from datetime import datetime

import pytest

from ophelos_sdk.models import Tenant


class TestTenant:
    """Test cases for Tenant model."""

    def test_tenant_creation_minimal(self):
        """Test tenant creation with minimal required fields."""
        tenant = Tenant(name="Test Tenant")
        
        assert tenant.id is None
        assert tenant.object == "tenant"
        assert tenant.name == "Test Tenant"
        assert tenant.description is None
        assert tenant.configurations == {}
        assert tenant.metadata is None
        assert tenant.created_at is None
        assert tenant.updated_at is None

    def test_tenant_creation_with_all_fields(self):
        """Test tenant creation with all fields."""
        created_time = datetime.now()
        updated_time = datetime.now()
        
        tenant = Tenant(
            id="tenant_123",
            object="tenant",
            name="Full Test Tenant",
            description="A comprehensive test tenant for testing purposes",
            configurations={
                "api_version": "v2",
                "features": ["feature_a", "feature_b"]
            },
            metadata={
                "environment": "test",
                "region": "eu-west-1"
            },
            created_at=created_time,
            updated_at=updated_time
        )
        
        assert tenant.id == "tenant_123"
        assert tenant.object == "tenant"
        assert tenant.name == "Full Test Tenant"
        assert tenant.description == "A comprehensive test tenant for testing purposes"
        assert tenant.configurations == {
            "api_version": "v2",
            "features": ["feature_a", "feature_b"]
        }
        assert tenant.metadata == {
            "environment": "test",
            "region": "eu-west-1"
        }
        assert tenant.created_at == created_time
        assert tenant.updated_at == updated_time

    def test_tenant_with_complex_metadata(self):
        """Test tenant creation with complex metadata."""
        complex_configurations = {
            "api_version": "v2",
            "rate_limits": {
                "requests_per_minute": 1000,
                "burst_limit": 50
            },
            "integrations": ["webhook", "email", "sms"],
            "features": {
                "advanced_reporting": True,
                "custom_branding": False,
                "multi_currency": True
            }
        }
        
        tenant = Tenant(
            name="Complex Tenant",
            description="Tenant with complex configurations",
            configurations=complex_configurations,
            metadata={"environment": "test"}
        )
        
        assert tenant.name == "Complex Tenant"
        assert tenant.configurations == complex_configurations
        assert tenant.configurations["api_version"] == "v2"
        assert tenant.configurations["features"]["advanced_reporting"] is True
        assert tenant.metadata == {"environment": "test"}

    def test_tenant_to_api_body_basic(self):
        """Test tenant to_api_body with basic fields."""
        tenant = Tenant(
            id="tenant_api_test",
            object="tenant",
            name="API Test Tenant",
            description="Tenant for API body testing",
            configurations={"test_mode": True},
            metadata={"test": True, "priority": "high"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        api_body = tenant.to_api_body()
        
        # Server fields should be excluded
        assert "id" not in api_body
        assert "object" not in api_body
        assert "created_at" not in api_body
        assert "updated_at" not in api_body
        
        # Client fields should be included
        assert api_body["name"] == "API Test Tenant"
        assert api_body["description"] == "Tenant for API body testing"
        assert api_body["configurations"] == {"test_mode": True}
        assert api_body["metadata"] == {"test": True, "priority": "high"}

    def test_tenant_to_api_body_exclude_none_false(self):
        """Test tenant to_api_body includes None values when exclude_none=False."""
        tenant = Tenant(
            name="Include None Tenant",
            description=None,
            metadata=None
        )
        
        api_body = tenant.to_api_body(exclude_none=False)
        
        assert api_body["name"] == "Include None Tenant"
        # None values should be included
        assert "description" in api_body
        assert api_body["description"] is None
        assert "metadata" in api_body
        assert api_body["metadata"] is None
        # Empty dict should be included
        assert api_body["configurations"] == {}

    def test_tenant_configurations_formats(self):
        """Test tenant with different configuration formats."""
        config_cases = [
            {"simple": "value"},
            {"nested": {"key": "value"}},
            {"list": [1, 2, 3]},
            {"mixed": {"string": "value", "number": 123, "boolean": True}},
            {"empty": {}}
        ]
        
        for config in config_cases:
            tenant = Tenant(
                name="Test Tenant",
                configurations=config
            )
            
            assert tenant.configurations == config
            
            api_body = tenant.to_api_body()
            assert api_body["configurations"] == config

    def test_tenant_long_description(self):
        """Test tenant with long description."""
        long_description = (
            "This is a very long description for a tenant that might contain "
            "multiple sentences and detailed information about the tenant's "
            "purpose, configuration, and usage. It should be properly handled "
            "by the model and included in the API body when creating or updating "
            "the tenant through the API."
        )
        
        tenant = Tenant(
            name="Long Description Tenant",
            description=long_description
        )
        
        assert tenant.description == long_description
        
        api_body = tenant.to_api_body()
        assert api_body["description"] == long_description

    def test_tenant_empty_metadata(self):
        """Test tenant with empty metadata dictionary."""
        tenant = Tenant(
            name="Empty Metadata Tenant",
            metadata={}
        )
        
        assert tenant.metadata == {}
        
        api_body = tenant.to_api_body()
        assert api_body["metadata"] == {}

    def test_tenant_name_variations(self):
        """Test tenant with various name formats."""
        name_cases = [
            "Simple Name",
            "Name with Numbers 123",
            "Name-with-Hyphens",
            "Name_with_Underscores",
            "Name with Special Characters & Symbols!",
            "Very Long Tenant Name That Might Be Used In Real World Scenarios",
            "短い名前",  # Short name in Japanese
            "Nom avec accents éàù"  # Name with accents
        ]
        
        for name in name_cases:
            tenant = Tenant(name=name)
            
            assert tenant.name == name
            
            api_body = tenant.to_api_body()
            assert api_body["name"] == name

    def test_tenant_metadata_serialization(self):
        """Test that complex metadata is properly serialized in API body."""
        metadata = {
            "strings": "test",
            "numbers": 42,
            "booleans": True,
            "lists": [1, 2, 3],
            "nested": {
                "level1": {
                    "level2": "deep_value"
                }
            },
            "null_value": None
        }
        
        tenant = Tenant(
            name="Metadata Test Tenant",
            metadata=metadata
        )
        
        api_body = tenant.to_api_body()
        
        # Metadata should be preserved as-is
        assert api_body["metadata"] == metadata
        assert api_body["metadata"]["nested"]["level1"]["level2"] == "deep_value"
        assert api_body["metadata"]["null_value"] is None 