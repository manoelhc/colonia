"""Tests for Context API endpoints."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.api import validate_context_data


def test_validate_context_data():
    """Test context data validation."""
    # Valid data
    valid_data = {
        "name": "Test Context",
        "description": "A test context",
        "project_id": 1
    }
    is_valid, error = validate_context_data(valid_data)
    assert is_valid is True
    assert error is None
    
    # Missing name
    invalid_data = {"project_id": 1}
    is_valid, error = validate_context_data(invalid_data)
    assert is_valid is False
    assert "required" in error.lower()
    
    # Empty name
    invalid_data = {"name": "", "project_id": 1}
    is_valid, error = validate_context_data(invalid_data)
    assert is_valid is False
    assert "empty" in error.lower()
    
    # Name too long
    invalid_data = {"name": "A" * 256, "project_id": 1}
    is_valid, error = validate_context_data(invalid_data)
    assert is_valid is False
    assert "too long" in error.lower()
    
    # Description too long
    invalid_data = {
        "name": "Test",
        "description": "A" * 1001,
        "project_id": 1
    }
    is_valid, error = validate_context_data(invalid_data)
    assert is_valid is False
    assert "description" in error.lower() and "too long" in error.lower()
    
    # Missing project_id
    invalid_data = {"name": "Test"}
    is_valid, error = validate_context_data(invalid_data)
    assert is_valid is False
    assert "project" in error.lower()
    
    # Invalid project_id type
    invalid_data = {"name": "Test", "project_id": "invalid"}
    is_valid, error = validate_context_data(invalid_data)
    assert is_valid is False
    assert "invalid" in error.lower()
    
    # Valid data with optional description
    valid_data = {
        "name": "Test Context",
        "project_id": 1
    }
    is_valid, error = validate_context_data(valid_data)
    assert is_valid is True
    assert error is None


def test_context_name_sanitization():
    """Test that context names are properly sanitized."""
    from app.api import sanitize_string
    
    # Normal name
    assert sanitize_string("My Context") == "My Context"
    
    # Name with whitespace
    assert sanitize_string("  My Context  ") == "My Context"
    
    # Name with null bytes
    assert sanitize_string("My\x00Context") == "MyContext"
    
    # Name with max length
    assert sanitize_string("A" * 300, max_length=255) == "A" * 255


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
