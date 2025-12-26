"""Tests for the stats API endpoint."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from unittest.mock import MagicMock, patch
from app.api import get_stats_handler


def test_get_stats_handler_success():
    """Test successful stats retrieval."""
    # Mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Mock the database session
    with patch('app.api.get_session') as mock_get_session:
        # Create a mock session context manager
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock the exec method to return counts
        mock_session.exec.return_value.one.side_effect = [2, 3, 3]  # projects, stacks, environments
        
        # Call the handler
        response = get_stats_handler(mock_request, mock_app)
        
        # Parse the response
        stats = json.loads(response.body)
        
        # Verify the response
        assert response.status == 200
        assert stats['projects'] == 2
        assert stats['stacks'] == 3
        assert stats['environments'] == 3
        assert stats['runs'] == 0
        assert stats['resources'] == 0


def test_get_stats_handler_error():
    """Test error handling in stats retrieval."""
    # Mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Mock the database session to raise an exception
    with patch('app.api.get_session') as mock_get_session:
        mock_get_session.return_value.__enter__.side_effect = Exception("Database error")
        
        # Call the handler
        response = get_stats_handler(mock_request, mock_app)
        
        # Verify error response
        assert response.status == 500
        result = json.loads(response.body)
        assert 'error' in result
        assert 'Database error' in result['error']
