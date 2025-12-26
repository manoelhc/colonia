"""Tests for repo-scan functionality."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
import tempfile
import yaml


# Import after path is set
import importlib.util
spec = importlib.util.spec_from_file_location("repo_scan", os.path.join(os.path.dirname(__file__), '..', 'repo-scan.py'))
repo_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repo_scan)


@patch('requests.get')
def test_fetch_colonia_yaml_success(mock_get):
    """Test successful fetching of colonia.yaml from GitHub."""
    # Mock response
    yaml_content = """
environments:
  - name: development
    dir: example/environments/development
stacks:
  - name: VPC
    environments:
      - development
    stack: stacks/vpc
"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = yaml_content
    mock_get.return_value = mock_response

    # Call function
    result = repo_scan.fetch_colonia_yaml("https://github.com/user/repo")

    # Assertions
    assert result is not None
    assert 'environments' in result
    assert 'stacks' in result
    assert len(result['environments']) == 1
    assert result['environments'][0]['name'] == 'development'


@patch('requests.get')
def test_fetch_colonia_yaml_not_found(mock_get):
    """Test handling when colonia.yaml is not found."""
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    # Call function
    result = repo_scan.fetch_colonia_yaml("https://github.com/user/repo")

    # Assertions
    assert result is None


@patch('requests.get')
def test_fetch_colonia_yaml_invalid_yaml(mock_get):
    """Test handling of invalid YAML content."""
    # Mock response with invalid YAML
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "invalid: yaml: content: ["
    mock_get.return_value = mock_response

    # Call function
    result = repo_scan.fetch_colonia_yaml("https://github.com/user/repo")

    # Assertions
    assert result is None


def test_fetch_colonia_yaml_no_url():
    """Test handling when no URL is provided."""
    result = repo_scan.fetch_colonia_yaml(None)
    assert result is None

    result = repo_scan.fetch_colonia_yaml("")
    assert result is None
