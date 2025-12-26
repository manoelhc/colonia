"""API routes and handlers for Colonia."""

import json
import re
import logging
from datetime import datetime
from typing import Optional
from rupy import Request, Response
from sqlmodel import select, func
from models import Project, Environment, Stack, StackEnvironment
from app.database import get_session
from app.rabbitmq import send_project_scan_message

# Get logger without configuring it at module level
logger = logging.getLogger(__name__)


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
    try:
        # Parse request body
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)

        # Validate input data
        is_valid, error_message = validate_project_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
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

            # Send message to RabbitMQ for repo scan
            if repository_url:
                try:
                    success = send_project_scan_message(project.id, project.name, project.repository_url)
                    if not success:
                        logger.warning(f"Failed to send RabbitMQ message for project {project.id}")
                except Exception as e:
                    logger.error(f"Exception while sending RabbitMQ message for project {project.id}: {e}", exc_info=True)

            # Return created project
            response_body = json.dumps(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )
            response = Response(response_body, status=201)
            response.set_header("Content-Type", "application/json")
            return response

    except json.JSONDecodeError:
        response = Response(
            json.dumps({"error": "Invalid JSON in request body"}), status=400
        )
        response.set_header("Content-Type", "application/json")
        return response
    except Exception as e:
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def list_projects_handler(request: Request, app) -> Response:
    """List all projects."""
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

            response = Response(json.dumps({"projects": projects_data}), status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def get_project_handler(request: Request, app, project_id: str) -> Response:
    """Get a single project by ID."""
    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid project ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response = Response(
                    json.dumps({"error": "Project not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            response_body = json.dumps(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def update_project_handler(request: Request, app, project_id: str) -> Response:
    """Update a project."""
    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid project ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        # Parse request body
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)

        # Validate input data
        is_valid, error_message = validate_project_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response = Response(
                    json.dumps({"error": "Project not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
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

            response_body = json.dumps(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_url": project.repository_url,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
            )
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except json.JSONDecodeError:
        response = Response(
            json.dumps({"error": "Invalid JSON in request body"}), status=400
        )
        response.set_header("Content-Type", "application/json")
        return response
    except Exception as e:
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_project_handler(request: Request, app, project_id: str) -> Response:
    """Delete a project."""
    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid project ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response = Response(
                    json.dumps({"error": "Project not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            session.delete(project)

            response = Response(
                json.dumps({"message": "Project deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def trigger_repo_scan_handler(request: Request, app, project_id: str) -> Response:
    """Trigger a repository scan for a project."""
    try:
        # Validate project_id is an integer
        try:
            pid = int(project_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid project ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            project = session.get(Project, pid)

            if not project:
                response = Response(
                    json.dumps({"error": "Project not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Check if project has a repository URL
            if not project.repository_url:
                response = Response(
                    json.dumps({"error": "Project does not have a repository URL"}), 
                    status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Send message to RabbitMQ for repo scan
            try:
                success = send_project_scan_message(
                    project.id, project.name, project.repository_url
                )
                if not success:
                    logger.warning(f"Failed to send RabbitMQ message for project {project.id}")
                    response = Response(
                        json.dumps({"error": "Failed to trigger repository scan"}), 
                        status=500
                    )
                    response.set_header("Content-Type", "application/json")
                    return response
            except Exception as e:
                logger.error(
                    f"Exception while sending RabbitMQ message for project {project.id}: {e}", 
                    exc_info=True
                )
                response = Response(
                    json.dumps({"error": "Failed to trigger repository scan"}), 
                    status=500
                )
                response.set_header("Content-Type", "application/json")
                return response

            response = Response(
                json.dumps({"message": "Repository scan triggered successfully"}), 
                status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def get_stats_handler(request: Request, app) -> Response:
    """Get statistics for dashboard."""
    try:
        with get_session() as session:
            # Count projects
            projects_count = session.exec(select(func.count(Project.id))).one()
            
            # Count stacks
            stacks_count = session.exec(select(func.count(Stack.id))).one()
            
            # Count environments
            environments_count = session.exec(select(func.count(Environment.id))).one()

            stats_data = {
                "projects": projects_count,
                "stacks": stacks_count,
                "environments": environments_count,
                "runs": 0,  # Placeholder for future implementation
                "resources": 0,  # Placeholder for future implementation
            }

            response = Response(json.dumps(stats_data), status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def get_stacks_grouped_handler(request: Request, app) -> Response:
    """Get stacks grouped by project and environment."""
    try:
        with get_session() as session:
            # Fetch all projects
            projects = session.exec(select(Project).order_by(Project.name)).all()
            
            result = []
            
            for project in projects:
                # Fetch environments for this project
                environments = session.exec(
                    select(Environment)
                    .where(Environment.project_id == project.id)
                    .order_by(Environment.name)
                ).all()
                
                project_data = {
                    "id": project.id,
                    "name": project.name,
                    "environments": []
                }
                
                for environment in environments:
                    # Fetch stacks for this environment
                    stacks = session.exec(
                        select(Stack)
                        .join(StackEnvironment, Stack.id == StackEnvironment.stack_id)
                        .where(StackEnvironment.environment_id == environment.id)
                        .where(Stack.project_id == project.id)
                        .order_by(Stack.name)
                    ).all()
                    
                    stacks_data = [
                        {
                            "id": stack.id,
                            "name": stack.name,
                            "stack_id": stack.stack_id,
                            "stack_path": stack.stack_path,
                            "depends_on": stack.depends_on or [],
                        }
                        for stack in stacks
                    ]
                    
                    project_data["environments"].append({
                        "id": environment.id,
                        "name": environment.name,
                        "stacks": stacks_data
                    })
                
                # Only add project if it has environments with stacks
                if any(env["stacks"] for env in project_data["environments"]):
                    result.append(project_data)

            response = Response(json.dumps({"projects": result}), status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error fetching grouped stacks: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response
