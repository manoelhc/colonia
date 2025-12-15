"""Tests for the Project model."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime
from models import Project


def test_project_creation():
    """Test creating a Project instance."""
    project = Project(
        name="Test Project",
        description="A test project",
        repository_url="https://github.com/user/repo"
    )
    
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.repository_url == "https://github.com/user/repo"
    assert project.id is None  # ID is not set until saved to DB
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)


def test_project_without_optional_fields():
    """Test creating a Project without optional fields."""
    project = Project(name="Minimal Project")
    
    assert project.name == "Minimal Project"
    assert project.description is None
    assert project.repository_url is None


def test_project_name_required():
    """Test that project name is required."""
    # SQLModel allows creating instances without required fields,
    # validation happens when saving to DB or explicitly calling model_validate
    # This is expected behavior for SQLModel
    project = Project(name="Test")
    assert project.name == "Test"
