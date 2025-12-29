"""Tests for the stacks grouped API endpoint."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from unittest.mock import MagicMock, patch
from app.api import get_stacks_grouped_handler


def test_get_stacks_grouped_handler_success():
    """Test successful grouped stacks retrieval."""
    # Mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Mock the database session
    with patch('app.api.get_session') as mock_get_session:
        # Create mock objects
        mock_project = MagicMock()
        mock_project.id = 1
        mock_project.name = "Test Project"
        
        mock_env = MagicMock()
        mock_env.id = 1
        mock_env.name = "development"
        
        mock_stack = MagicMock()
        mock_stack.id = 1
        mock_stack.name = "VPC"
        mock_stack.stack_id = "vpc"
        mock_stack.stack_path = "stacks/vpc"
        mock_stack.depends_on = None
        
        mock_stack_env = MagicMock()
        mock_stack_env.stack_id = 1
        mock_stack_env.environment_id = 1
        
        # Create a mock session context manager
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock the exec method to return mock data - now includes 4 queries per project
        mock_session.exec.return_value.all.side_effect = [
            [mock_project],     # projects query
            [mock_env],         # environments query for first project
            [mock_stack],       # stacks query for first project
            [mock_stack_env]    # stack-environment relationships query
        ]
        
        # Call the handler
        response = get_stacks_grouped_handler(mock_request, mock_app)
        
        # Parse the response
        result = json.loads(response.body)
        
        # Verify the response structure
        assert response.status == 200
        assert 'projects' in result
        assert len(result['projects']) == 1
        assert result['projects'][0]['name'] == "Test Project"
        assert len(result['projects'][0]['environments']) == 1
        assert result['projects'][0]['environments'][0]['name'] == "development"
        assert len(result['projects'][0]['environments'][0]['stacks']) == 1
        assert result['projects'][0]['environments'][0]['stacks'][0]['name'] == "VPC"


def test_get_stacks_grouped_handler_empty():
    """Test grouped stacks retrieval with no data."""
    # Mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Mock the database session
    with patch('app.api.get_session') as mock_get_session:
        # Create a mock session context manager
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock the exec method to return empty list
        mock_session.exec.return_value.all.return_value = []
        
        # Call the handler
        response = get_stacks_grouped_handler(mock_request, mock_app)
        
        # Parse the response
        result = json.loads(response.body)
        
        # Verify the response
        assert response.status == 200
        assert 'projects' in result
        assert len(result['projects']) == 0


def test_get_stacks_grouped_handler_error():
    """Test error handling in grouped stacks retrieval."""
    # Mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Mock the database session to raise an exception
    with patch('app.api.get_session') as mock_get_session:
        mock_get_session.return_value.__enter__.side_effect = Exception("Database error")
        
        # Call the handler
        response = get_stacks_grouped_handler(mock_request, mock_app)
        
        # Verify error response
        assert response.status == 500
        result = json.loads(response.body)
        assert 'error' in result
        assert 'Database error' in result['error']
