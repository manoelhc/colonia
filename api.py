"""API routes and handlers for Colonia."""

import json
import re
from datetime import datetime
from typing import Optional
from rupy import Request, Response
from sqlmodel import select
from models import Project
from database import get_session


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input by removing potentially harmful characters."""
    if not value:
        return ""

    # Remove null bytes
    value = value.replace("\x00", "")

    # Strip leading/trailing whitespace
    value = value.strip()

    # Apply max length if specified
    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def sanitize_url(url: str) -> Optional[str]:
    """Validate and sanitize URL input."""
    if not url:
        return None

    url = sanitize_string(url, max_length=500)

    # Basic URL validation regex
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        return None

    return url


def validate_project_data(data: dict) -> tuple[bool, Optional[str]]:
    """Validate project data."""
    # Check required fields
    if "name" not in data or not data["name"]:
        return False, "Project name is required"

    # Validate name length
    name = data["name"].strip()
    if len(name) < 1:
        return False, "Project name cannot be empty"
    if len(name) > 255:
        return False, "Project name is too long (max 255 characters)"

    # Validate description length if provided
    if "description" in data and data["description"]:
        if len(data["description"]) > 1000:
            return False, "Description is too long (max 1000 characters)"

    # Validate repository URL if provided
    if "repository_url" in data and data["repository_url"]:
        sanitized_url = sanitize_url(data["repository_url"])
        if sanitized_url is None:
            return False, "Invalid repository URL format"

    return True, None


def create_project_handler(request: Request, app) -> Response:
    """Create a new project."""
    response = Response()
    response.set_header("Content-Type", "application/json")

    try:
        # Parse request body
        body = request.body
        if not body:
            response.status = 400
            response.body = json.dumps({"error": "Request body is required"})
            return response

        data = json.loads(body)

        # Validate input data
        is_valid, error_message = validate_project_data(data)
        if not is_valid:
            response.status = 400
            response.body = json.dumps({"error": error_message})
            return response

        # Sanitize inputs
        name = sanitize_string(data["name"], max_length=255)
        description = (
            sanitize_string(data.get("description", ""), max_length=1000) or None
        )
        repository_url = sanitize_url(data.get("repository_url", ""))

        # Create project
        with get_session() as session:
            project = Project(
                name=name, description=description, repository_url=repository_url
            )
            session.add(project)
            session.flush()
            session.refresh(project)

            # Return created project
            response.status = 201
            response.body = json.dumps(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )

    except json.JSONDecodeError:
        response.status = 400
        response.body = json.dumps({"error": "Invalid JSON in request body"})
    except Exception as e:
        response.status = 500
        response.body = json.dumps({"error": f"Internal server error: {str(e)}"})

    return response


def list_projects_handler(request: Request, app) -> Response:
    """List all projects."""
    response = Response()
    response.set_header("Content-Type", "application/json")

    try:
        with get_session() as session:
            statement = select(Project).order_by(Project.created_at.desc())
            projects = session.exec(statement).all()

            projects_data = [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
                for project in projects
            ]

            response.status = 200
            response.body = json.dumps({"projects": projects_data})

    except Exception as e:
        response.status = 500
        response.body = json.dumps({"error": f"Internal server error: {str(e)}"})

    return response


def get_project_handler(request: Request, app, project_id: str) -> Response:
    """Get a single project by ID."""
    response = Response()
    response.set_header("Content-Type", "application/json")

    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response.status = 400
            response.body = json.dumps({"error": "Invalid project ID"})
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response.status = 404
                response.body = json.dumps({"error": "Project not found"})
                return response

            response.status = 200
            response.body = json.dumps(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )

    except Exception as e:
        response.status = 500
        response.body = json.dumps({"error": f"Internal server error: {str(e)}"})

    return response


def update_project_handler(request: Request, app, project_id: str) -> Response:
    """Update a project."""
    response = Response()
    response.set_header("Content-Type", "application/json")

    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response.status = 400
            response.body = json.dumps({"error": "Invalid project ID"})
            return response

        # Parse request body
        body = request.body
        if not body:
            response.status = 400
            response.body = json.dumps({"error": "Request body is required"})
            return response

        data = json.loads(body)

        # Validate input data
        is_valid, error_message = validate_project_data(data)
        if not is_valid:
            response.status = 400
            response.body = json.dumps({"error": error_message})
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response.status = 404
                response.body = json.dumps({"error": "Project not found"})
                return response

            # Update fields
            project.name = sanitize_string(data["name"], max_length=255)
            project.description = (
                sanitize_string(data.get("description", ""), max_length=1000) or None
            )
            project.repository_url = sanitize_url(data.get("repository_url", ""))
            project.updated_at = datetime.utcnow()

            session.add(project)
            session.flush()
            session.refresh(project)

            response.status = 200
            response.body = json.dumps(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )

    except json.JSONDecodeError:
        response.status = 400
        response.body = json.dumps({"error": "Invalid JSON in request body"})
    except Exception as e:
        response.status = 500
        response.body = json.dumps({"error": f"Internal server error: {str(e)}"})

    return response


def delete_project_handler(request: Request, app, project_id: str) -> Response:
    """Delete a project."""
    response = Response()
    response.set_header("Content-Type", "application/json")

    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response.status = 400
            response.body = json.dumps({"error": "Invalid project ID"})
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response.status = 404
                response.body = json.dumps({"error": "Project not found"})
                return response

            session.delete(project)

            response.status = 200
            response.body = json.dumps({"message": "Project deleted successfully"})

    except Exception as e:
        response.status = 500
        response.body = json.dumps({"error": f"Internal server error: {str(e)}"})

    return response
