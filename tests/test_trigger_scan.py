"""Tests for the trigger repo scan API endpoint."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from models import Project
from database import get_session


def test_trigger_scan_for_project_with_repo_url():
    """Test triggering scan for a project with repository URL."""
    # Create a test project with repository URL
    with get_session() as session:
        project = Project(
            name="Test Project with Repo",
            description="Test project",
            repository_url="https://github.com/user/repo"
        )
        session.add(project)
        session.flush()
        project_id = project.id

    # Mock the send_project_scan_message function
    with patch('api.send_project_scan_message') as mock_send:
        mock_send.return_value = True
        
        from api import trigger_repo_scan_handler
        from unittest.mock import MagicMock
        
        # Create mock request and app
        mock_request = MagicMock()
        mock_app = MagicMock()
        
        # Call the handler
        response = trigger_repo_scan_handler(mock_request, mock_app, str(project_id))
        
        # Assertions
        assert response.status == 200
        assert b"Repository scan triggered successfully" in response.body.encode() or "Repository scan triggered successfully" in response.body
        mock_send.assert_called_once()


def test_trigger_scan_for_project_without_repo_url():
    """Test triggering scan for a project without repository URL."""
    # Create a test project without repository URL
    with get_session() as session:
        project = Project(
            name="Test Project without Repo",
            description="Test project"
        )
        session.add(project)
        session.flush()
        project_id = project.id

    from api import trigger_repo_scan_handler
    from unittest.mock import MagicMock
    
    # Create mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Call the handler
    response = trigger_repo_scan_handler(mock_request, mock_app, str(project_id))
    
    # Assertions
    assert response.status == 400
    assert b"does not have a repository URL" in response.body.encode() or "does not have a repository URL" in response.body


def test_trigger_scan_for_nonexistent_project():
    """Test triggering scan for a non-existent project."""
    from api import trigger_repo_scan_handler
    from unittest.mock import MagicMock
    
    # Create mock request and app
    mock_request = MagicMock()
    mock_app = MagicMock()
    
    # Call the handler with non-existent project ID
    response = trigger_repo_scan_handler(mock_request, mock_app, "99999")
    
    # Assertions
    assert response.status == 404
    assert b"Project not found" in response.body.encode() or "Project not found" in response.body
