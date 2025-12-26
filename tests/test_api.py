"""Tests for API endpoints."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app.api import (
    sanitize_string,
    sanitize_url,
    validate_project_data
)


def test_sanitize_string():
    """Test string sanitization."""
    # Normal string
    assert sanitize_string("Hello World") == "Hello World"
    
    # String with null bytes
    assert sanitize_string("Hello\x00World") == "HelloWorld"
    
    # String with whitespace
    assert sanitize_string("  Hello World  ") == "Hello World"
    
    # String with max length
    assert sanitize_string("A" * 100, max_length=50) == "A" * 50
    
    # Empty string
    assert sanitize_string("") == ""
    
    # None value
    assert sanitize_string(None) == ""


def test_sanitize_url():
    """Test URL sanitization and validation."""
    # Valid HTTP URL
    assert sanitize_url("http://example.com") == "http://example.com"
    
    # Valid HTTPS URL
    assert sanitize_url("https://github.com/user/repo") == "https://github.com/user/repo"
    
    # Valid URL with port
    assert sanitize_url("http://localhost:8000") == "http://localhost:8000"
    
    # Valid URL with path
    assert sanitize_url("https://github.com/user/repo/tree/main") == "https://github.com/user/repo/tree/main"
    
    # Invalid URL (no protocol)
    assert sanitize_url("example.com") is None
    
    # Invalid URL (javascript protocol)
    assert sanitize_url("javascript:alert(1)") is None
    
    # Empty string
    assert sanitize_url("") is None
    
    # None value
    assert sanitize_url(None) is None


def test_validate_project_data():
    """Test project data validation."""
    # Valid data
    valid_data = {
        "name": "Test Project",
        "description": "A test project",
        "repository_url": "https://github.com/user/repo"
    }
    is_valid, error = validate_project_data(valid_data)
    assert is_valid is True
    assert error is None
    
    # Missing name
    invalid_data = {"description": "Test"}
    is_valid, error = validate_project_data(invalid_data)
    assert is_valid is False
    assert "required" in error.lower()
    
    # Empty name
    invalid_data = {"name": ""}
    is_valid, error = validate_project_data(invalid_data)
    assert is_valid is False
    assert "required" in error.lower() or "empty" in error.lower()
    
    # Name too long
    invalid_data = {"name": "A" * 300}
    is_valid, error = validate_project_data(invalid_data)
    assert is_valid is False
    assert "too long" in error.lower()
    
    # Description too long
    invalid_data = {
        "name": "Test",
        "description": "A" * 1100
    }
    is_valid, error = validate_project_data(invalid_data)
    assert is_valid is False
    assert "description" in error.lower()
    
    # Invalid URL
    invalid_data = {
        "name": "Test",
        "repository_url": "not-a-url"
    }
    is_valid, error = validate_project_data(invalid_data)
    assert is_valid is False
    assert "url" in error.lower()
    
    # Valid data with only name
    valid_data = {"name": "Simple Project"}
    is_valid, error = validate_project_data(valid_data)
    assert is_valid is True
    assert error is None
