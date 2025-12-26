"""Tests for Environment and Stack models."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime
from models import Project, Environment, Stack, StackEnvironment
from app.database import get_session


def test_environment_creation():
    """Test creating an Environment."""
    with get_session() as session:
        # Create a project first
        project = Project(
            name="Test Project",
            description="A test project",
            repository_url="https://github.com/user/repo"
        )
        session.add(project)
        session.flush()

        # Create an environment
        env = Environment(
            project_id=project.id,
            name="development",
            directory="example/environments/development"
        )
        session.add(env)
        session.flush()

        assert env.id is not None
        assert env.project_id == project.id
        assert env.name == "development"
        assert env.directory == "example/environments/development"
        assert isinstance(env.created_at, datetime)


def test_stack_creation():
    """Test creating a Stack."""
    with get_session() as session:
        # Create a project first
        project = Project(
            name="Test Project",
            description="A test project",
            repository_url="https://github.com/user/repo"
        )
        session.add(project)
        session.flush()

        # Create a stack
        stack = Stack(
            project_id=project.id,
            name="VPC",
            stack_path="stacks/vpc"
        )
        session.add(stack)
        session.flush()

        assert stack.id is not None
        assert stack.project_id == project.id
        assert stack.name == "VPC"
        assert stack.stack_path == "stacks/vpc"
        assert isinstance(stack.created_at, datetime)


def test_stack_environment_relationship():
    """Test creating a Stack-Environment relationship."""
    with get_session() as session:
        # Create a project first
        project = Project(
            name="Test Project",
            description="A test project",
            repository_url="https://github.com/user/repo"
        )
        session.add(project)
        session.flush()

        # Create an environment
        env = Environment(
            project_id=project.id,
            name="development",
            directory="example/environments/development"
        )
        session.add(env)
        session.flush()

        # Create a stack
        stack = Stack(
            project_id=project.id,
            name="VPC",
            stack_path="stacks/vpc"
        )
        session.add(stack)
        session.flush()

        # Create relationship
        stack_env = StackEnvironment(
            stack_id=stack.id,
            environment_id=env.id
        )
        session.add(stack_env)
        session.flush()

        assert stack_env.stack_id == stack.id
        assert stack_env.environment_id == env.id
