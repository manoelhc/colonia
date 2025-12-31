"""API routes and handlers for Colonia."""

import json
import re
import logging
from datetime import datetime
from typing import Optional
from rupy import Request, Response
from sqlmodel import select, func
from models import Project, Environment, Stack, StackEnvironment, User, Team, TeamMember, TeamPermission, Context, ContextSecret, ContextEnvVar
from app.database import get_session
from app.rabbitmq import send_project_scan_message
from app.config import get_vault_config, set_vault_config
from app.vault import test_vault_connection, list_secrets_engines, enable_secrets_engine

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
                
                # Fetch all stacks for this project
                project_stacks = session.exec(
                    select(Stack)
                    .where(Stack.project_id == project.id)
                    .order_by(Stack.name)
                ).all()
                
                # Fetch all stack-environment relationships for this project
                stack_env_relationships = session.exec(
                    select(StackEnvironment)
                    .where(StackEnvironment.stack_id.in_([s.id for s in project_stacks]))
                ).all()
                
                # Create a mapping of environment_id to stack_ids
                env_to_stacks = {}
                for rel in stack_env_relationships:
                    if rel.environment_id not in env_to_stacks:
                        env_to_stacks[rel.environment_id] = []
                    env_to_stacks[rel.environment_id].append(rel.stack_id)
                
                # Create a mapping of stack_id to stack object
                stacks_by_id = {stack.id: stack for stack in project_stacks}
                
                project_data = {
                    "id": project.id,
                    "name": project.name,
                    "environments": []
                }
                
                for environment in environments:
                    # Get stacks for this environment
                    stack_ids = env_to_stacks.get(environment.id, [])
                    stacks = [stacks_by_id[sid] for sid in stack_ids if sid in stacks_by_id]
                    
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
                    
                    if stacks_data:
                        project_data["environments"].append({
                            "id": environment.id,
                            "name": environment.name,
                            "stacks": stacks_data
                        })
                
                # Only add project if it has environments with stacks
                if project_data["environments"]:
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


def get_environments_grouped_handler(request: Request, app) -> Response:
    """Get environments grouped by project."""
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
                
                if environments:
                    environments_data = [
                        {
                            "id": environment.id,
                            "name": environment.name,
                            "directory": environment.directory,
                            "created_at": environment.created_at.isoformat(),
                            "updated_at": environment.updated_at.isoformat(),
                        }
                        for environment in environments
                    ]
                    
                    result.append({
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "repository_url": project.repository_url,
                        "environments": environments_data
                    })

            response = Response(json.dumps({"projects": result}), status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error fetching grouped environments: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


# User API Handlers
def sanitize_email(email: str) -> Optional[str]:
    """Validate and sanitize email input."""
    if not email:
        return None

    email = sanitize_string(email, max_length=255)
    
    # Basic email validation regex
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    
    if not email_pattern.match(email):
        return None
    
    return email.lower()


def validate_user_data(data: dict) -> tuple[bool, Optional[str]]:
    """Validate user data."""
    if "username" not in data or not data["username"]:
        return False, "Username is required"
    
    if "email" not in data or not data["email"]:
        return False, "Email is required"
    
    if "name" not in data or not data["name"]:
        return False, "Name is required"
    
    username = data["username"].strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 100:
        return False, "Username is too long (max 100 characters)"
    
    if len(data["name"]) > 255:
        return False, "Name is too long (max 255 characters)"
    
    if sanitize_email(data["email"]) is None:
        return False, "Invalid email format"
    
    return True, None


def create_user_handler(request: Request, app) -> Response:
    """Create a new user."""
    try:
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        is_valid, error_message = validate_user_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        username = sanitize_string(data["username"], max_length=100).lower()
        email = sanitize_email(data["email"])
        name = sanitize_string(data["name"], max_length=255)

        with get_session() as session:
            # Check if username already exists
            existing_user = session.exec(
                select(User).where(User.username == username)
            ).first()
            if existing_user:
                response = Response(
                    json.dumps({"error": "Username already exists"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response
            
            # Check if email already exists
            existing_email = session.exec(
                select(User).where(User.email == email)
            ).first()
            if existing_email:
                response = Response(
                    json.dumps({"error": "Email already exists"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            user = User(username=username, email=email, name=name)
            session.add(user)
            session.flush()
            session.refresh(user)

            response_body = json.dumps({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            })
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
        logger.error(f"Error creating user: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def list_users_handler(request: Request, app) -> Response:
    """List all users."""
    try:
        with get_session() as session:
            statement = select(User).order_by(User.created_at.desc())
            users = session.exec(statement).all()

            users_data = [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                }
                for user in users
            ]

            response = Response(json.dumps({"users": users_data}), status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def get_user_handler(request: Request, app, user_id: str) -> Response:
    """Get a single user by ID."""
    try:
        try:
            uid = int(user_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid user ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            user = session.get(User, uid)

            if not user:
                response = Response(
                    json.dumps({"error": "User not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            response_body = json.dumps({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            })
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error getting user: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def update_user_handler(request: Request, app, user_id: str) -> Response:
    """Update a user."""
    try:
        try:
            uid = int(user_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid user ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        is_valid, error_message = validate_user_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            user = session.get(User, uid)

            if not user:
                response = Response(
                    json.dumps({"error": "User not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            username = sanitize_string(data["username"], max_length=100).lower()
            email = sanitize_email(data["email"])
            
            # Check if username is taken by another user
            if username != user.username:
                existing_user = session.exec(
                    select(User).where(User.username == username)
                ).first()
                if existing_user:
                    response = Response(
                        json.dumps({"error": "Username already exists"}), status=400
                    )
                    response.set_header("Content-Type", "application/json")
                    return response
            
            # Check if email is taken by another user
            if email != user.email:
                existing_email = session.exec(
                    select(User).where(User.email == email)
                ).first()
                if existing_email:
                    response = Response(
                        json.dumps({"error": "Email already exists"}), status=400
                    )
                    response.set_header("Content-Type", "application/json")
                    return response

            user.username = username
            user.email = email
            user.name = sanitize_string(data["name"], max_length=255)
            user.updated_at = datetime.utcnow()

            session.add(user)
            session.flush()
            session.refresh(user)

            response_body = json.dumps({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            })
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
        logger.error(f"Error updating user: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_user_handler(request: Request, app, user_id: str) -> Response:
    """Delete a user and all associated team memberships."""
    try:
        try:
            uid = int(user_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid user ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            user = session.get(User, uid)

            if not user:
                response = Response(
                    json.dumps({"error": "User not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Delete all team memberships for this user first
            team_members = session.exec(
                select(TeamMember).where(TeamMember.user_id == uid)
            ).all()
            for member in team_members:
                session.delete(member)

            # Now delete the user
            session.delete(user)

            response = Response(
                json.dumps({"message": "User deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


# Team API Handlers
def validate_team_data(data: dict) -> tuple[bool, Optional[str]]:
    """Validate team data."""
    if "name" not in data or not data["name"]:
        return False, "Team name is required"
    
    name = data["name"].strip()
    if len(name) < 1:
        return False, "Team name cannot be empty"
    if len(name) > 255:
        return False, "Team name is too long (max 255 characters)"
    
    if "description" in data and data["description"]:
        if len(data["description"]) > 1000:
            return False, "Description is too long (max 1000 characters)"
    
    return True, None


def create_team_handler(request: Request, app) -> Response:
    """Create a new team."""
    try:
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        is_valid, error_message = validate_team_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        name = sanitize_string(data["name"], max_length=255)
        description = sanitize_string(data.get("description", ""), max_length=1000) or None

        with get_session() as session:
            # Check if team name already exists
            existing_team = session.exec(
                select(Team).where(Team.name == name)
            ).first()
            if existing_team:
                response = Response(
                    json.dumps({"error": "Team name already exists"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            team = Team(name=name, description=description)
            session.add(team)
            session.flush()
            session.refresh(team)

            response_body = json.dumps({
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "created_at": team.created_at.isoformat(),
                "updated_at": team.updated_at.isoformat(),
            })
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
        logger.error(f"Error creating team: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def list_teams_handler(request: Request, app) -> Response:
    """List all teams with their members and permissions."""
    try:
        with get_session() as session:
            teams = session.exec(select(Team).order_by(Team.created_at.desc())).all()

            teams_data = []
            for team in teams:
                # Get team members
                members = session.exec(
                    select(TeamMember, User)
                    .join(User, TeamMember.user_id == User.id)
                    .where(TeamMember.team_id == team.id)
                ).all()
                
                members_data = [
                    {
                        "id": member.id,
                        "user_id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "email": user.email,
                        "role": member.role,
                    }
                    for member, user in members
                ]
                
                # Get team permissions
                permissions = session.exec(
                    select(TeamPermission)
                    .where(TeamPermission.team_id == team.id)
                ).all()
                
                permissions_data = [
                    {
                        "id": perm.id,
                        "resource_type": perm.resource_type,
                        "resource_id": perm.resource_id,
                        "can_view": perm.can_view,
                        "can_plan": perm.can_plan,
                        "can_apply": perm.can_apply,
                        "all_stacks": perm.all_stacks,
                        "can_view_dependencies": perm.can_view_dependencies,
                        "can_plan_dependencies": perm.can_plan_dependencies,
                        "can_apply_dependencies": perm.can_apply_dependencies,
                    }
                    for perm in permissions
                ]
                
                teams_data.append({
                    "id": team.id,
                    "name": team.name,
                    "description": team.description,
                    "created_at": team.created_at.isoformat(),
                    "updated_at": team.updated_at.isoformat(),
                    "members": members_data,
                    "permissions": permissions_data,
                })

            response = Response(json.dumps({"teams": teams_data}), status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error listing teams: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def get_team_handler(request: Request, app, team_id: str) -> Response:
    """Get a single team by ID with members and permissions."""
    try:
        try:
            tid = int(team_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid team ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            team = session.get(Team, tid)

            if not team:
                response = Response(
                    json.dumps({"error": "Team not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Get team members
            members = session.exec(
                select(TeamMember, User)
                .join(User, TeamMember.user_id == User.id)
                .where(TeamMember.team_id == team.id)
            ).all()
            
            members_data = [
                {
                    "id": member.id,
                    "user_id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "email": user.email,
                    "role": member.role,
                }
                for member, user in members
            ]
            
            # Get team permissions
            permissions = session.exec(
                select(TeamPermission)
                .where(TeamPermission.team_id == team.id)
            ).all()
            
            permissions_data = [
                {
                    "id": perm.id,
                    "resource_type": perm.resource_type,
                    "resource_id": perm.resource_id,
                    "can_view": perm.can_view,
                    "can_plan": perm.can_plan,
                    "can_apply": perm.can_apply,
                    "all_stacks": perm.all_stacks,
                    "can_view_dependencies": perm.can_view_dependencies,
                    "can_plan_dependencies": perm.can_plan_dependencies,
                    "can_apply_dependencies": perm.can_apply_dependencies,
                }
                for perm in permissions
            ]

            response_body = json.dumps({
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "created_at": team.created_at.isoformat(),
                "updated_at": team.updated_at.isoformat(),
                "members": members_data,
                "permissions": permissions_data,
            })
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error getting team: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def update_team_handler(request: Request, app, team_id: str) -> Response:
    """Update a team."""
    try:
        try:
            tid = int(team_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid team ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        is_valid, error_message = validate_team_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            team = session.get(Team, tid)

            if not team:
                response = Response(
                    json.dumps({"error": "Team not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            name = sanitize_string(data["name"], max_length=255)
            
            # Check if team name is taken by another team
            if name != team.name:
                existing_team = session.exec(
                    select(Team).where(Team.name == name)
                ).first()
                if existing_team:
                    response = Response(
                        json.dumps({"error": "Team name already exists"}), status=400
                    )
                    response.set_header("Content-Type", "application/json")
                    return response

            team.name = name
            team.description = sanitize_string(data.get("description", ""), max_length=1000) or None
            team.updated_at = datetime.utcnow()

            session.add(team)
            session.flush()
            session.refresh(team)

            response_body = json.dumps({
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "created_at": team.created_at.isoformat(),
                "updated_at": team.updated_at.isoformat(),
            })
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
        logger.error(f"Error updating team: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_team_handler(request: Request, app, team_id: str) -> Response:
    """Delete a team and all associated members and permissions."""
    try:
        try:
            tid = int(team_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid team ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            team = session.get(Team, tid)

            if not team:
                response = Response(
                    json.dumps({"error": "Team not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Delete all team members first
            team_members = session.exec(
                select(TeamMember).where(TeamMember.team_id == tid)
            ).all()
            for member in team_members:
                session.delete(member)

            # Delete all team permissions
            team_permissions = session.exec(
                select(TeamPermission).where(TeamPermission.team_id == tid)
            ).all()
            for permission in team_permissions:
                session.delete(permission)

            # Now delete the team
            session.delete(team)

            response = Response(
                json.dumps({"message": "Team deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error deleting team: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def add_team_member_handler(request: Request, app, team_id: str) -> Response:
    """Add a member to a team."""
    try:
        try:
            tid = int(team_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid team ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        if "user_id" not in data:
            response = Response(
                json.dumps({"error": "user_id is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        try:
            uid = int(data["user_id"])
        except ValueError:
            response = Response(json.dumps({"error": "Invalid user ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        role = data.get("role", "member")
        if role not in ["member", "admin"]:
            response = Response(
                json.dumps({"error": "Role must be 'member' or 'admin'"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Check if team exists
            team = session.get(Team, tid)
            if not team:
                response = Response(
                    json.dumps({"error": "Team not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Check if user exists
            user = session.get(User, uid)
            if not user:
                response = Response(
                    json.dumps({"error": "User not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Check if member already exists
            existing_member = session.exec(
                select(TeamMember)
                .where(TeamMember.team_id == tid)
                .where(TeamMember.user_id == uid)
            ).first()
            
            if existing_member:
                response = Response(
                    json.dumps({"error": "User is already a member of this team"}), 
                    status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            member = TeamMember(team_id=tid, user_id=uid, role=role)
            session.add(member)
            session.flush()
            session.refresh(member)

            response_body = json.dumps({
                "id": member.id,
                "team_id": member.team_id,
                "user_id": member.user_id,
                "role": member.role,
                "created_at": member.created_at.isoformat(),
            })
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
        logger.error(f"Error adding team member: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def remove_team_member_handler(request: Request, app, team_id: str, member_id: str) -> Response:
    """Remove a member from a team."""
    try:
        try:
            tid = int(team_id)
            mid = int(member_id)
        except ValueError:
            response = Response(
                json.dumps({"error": "Invalid team or member ID"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            member = session.get(TeamMember, mid)

            if not member or member.team_id != tid:
                response = Response(
                    json.dumps({"error": "Team member not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            session.delete(member)

            response = Response(
                json.dumps({"message": "Team member removed successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error removing team member: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def set_team_permission_handler(request: Request, app, team_id: str) -> Response:
    """Set or update a team permission."""
    try:
        try:
            tid = int(team_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid team ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        required_fields = ["resource_type", "resource_id"]
        for field in required_fields:
            if field not in data:
                response = Response(
                    json.dumps({"error": f"{field} is required"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

        resource_type = data["resource_type"]
        if resource_type not in ["project", "environment", "stack"]:
            response = Response(
                json.dumps({"error": "resource_type must be 'project', 'environment', or 'stack'"}),
                status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        try:
            resource_id = int(data["resource_id"])
        except ValueError:
            response = Response(
                json.dumps({"error": "Invalid resource_id"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        can_view = data.get("can_view", True)
        can_plan = data.get("can_plan", False)
        can_apply = data.get("can_apply", False)
        all_stacks = data.get("all_stacks", False)
        can_view_dependencies = data.get("can_view_dependencies", False)
        can_plan_dependencies = data.get("can_plan_dependencies", False)
        can_apply_dependencies = data.get("can_apply_dependencies", False)

        with get_session() as session:
            # Check if team exists
            team = session.get(Team, tid)
            if not team:
                response = Response(
                    json.dumps({"error": "Team not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Check if permission already exists
            existing_perm = session.exec(
                select(TeamPermission)
                .where(TeamPermission.team_id == tid)
                .where(TeamPermission.resource_type == resource_type)
                .where(TeamPermission.resource_id == resource_id)
            ).first()
            
            if existing_perm:
                # Update existing permission
                existing_perm.can_view = can_view
                existing_perm.can_plan = can_plan
                existing_perm.can_apply = can_apply
                existing_perm.all_stacks = all_stacks
                existing_perm.can_view_dependencies = can_view_dependencies
                existing_perm.can_plan_dependencies = can_plan_dependencies
                existing_perm.can_apply_dependencies = can_apply_dependencies
                existing_perm.updated_at = datetime.utcnow()
                session.add(existing_perm)
                session.flush()
                session.refresh(existing_perm)
                permission = existing_perm
            else:
                # Create new permission
                permission = TeamPermission(
                    team_id=tid,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    can_view=can_view,
                    can_plan=can_plan,
                    can_apply=can_apply,
                    all_stacks=all_stacks,
                    can_view_dependencies=can_view_dependencies,
                    can_plan_dependencies=can_plan_dependencies,
                    can_apply_dependencies=can_apply_dependencies
                )
                session.add(permission)
                session.flush()
                session.refresh(permission)

            response_body = json.dumps({
                "id": permission.id,
                "team_id": permission.team_id,
                "resource_type": permission.resource_type,
                "resource_id": permission.resource_id,
                "can_view": permission.can_view,
                "can_plan": permission.can_plan,
                "can_apply": permission.can_apply,
                "all_stacks": permission.all_stacks,
                "can_view_dependencies": permission.can_view_dependencies,
                "can_plan_dependencies": permission.can_plan_dependencies,
                "can_apply_dependencies": permission.can_apply_dependencies,
                "created_at": permission.created_at.isoformat(),
                "updated_at": permission.updated_at.isoformat(),
            })
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
        logger.error(f"Error setting team permission: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_team_permission_handler(request: Request, app, team_id: str, permission_id: str) -> Response:
    """Delete a team permission."""
    try:
        try:
            tid = int(team_id)
            pid = int(permission_id)
        except ValueError:
            response = Response(
                json.dumps({"error": "Invalid team or permission ID"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            permission = session.get(TeamPermission, pid)

            if not permission or permission.team_id != tid:
                response = Response(
                    json.dumps({"error": "Team permission not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            session.delete(permission)

            response = Response(
                json.dumps({"message": "Team permission deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error deleting team permission: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


# Vault API Handlers
def get_vault_config_handler(request: Request, app) -> Response:
    """Get the current Vault configuration."""
    try:
        vault_config = get_vault_config()
        
        if vault_config:
            # Don't send the token back to the client, just indicate if it's set
            response_data = {
                "url": vault_config.get("url", ""),
                "token_set": bool(vault_config.get("token")),
                "namespace": vault_config.get("namespace", "")
            }
        else:
            response_data = {
                "url": "",
                "token_set": False,
                "namespace": ""
            }
        
        response = Response(json.dumps(response_data), status=200)
        response.set_header("Content-Type", "application/json")
        return response
        
    except Exception as e:
        logger.error(f"Error getting vault config: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def save_vault_config_handler(request: Request, app) -> Response:
    """Save Vault configuration."""
    try:
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        # Validate required fields
        if "url" not in data or not data["url"]:
            response = Response(
                json.dumps({"error": "Vault URL is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        if "token" not in data or not data["token"]:
            response = Response(
                json.dumps({"error": "Vault token is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        # Sanitize inputs
        vault_url = sanitize_url(data["url"])
        if not vault_url:
            response = Response(
                json.dumps({"error": "Invalid Vault URL format"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        vault_token = sanitize_string(data["token"], max_length=500)
        vault_namespace = sanitize_string(data.get("namespace", ""), max_length=255) or None
        
        # Save configuration
        success = set_vault_config(vault_url, vault_token, vault_namespace)
        
        if success:
            response = Response(
                json.dumps({"message": "Vault configuration saved successfully"}), 
                status=200
            )
            response.set_header("Content-Type", "application/json")
            return response
        else:
            response = Response(
                json.dumps({"error": "Failed to save Vault configuration"}), 
                status=500
            )
            response.set_header("Content-Type", "application/json")
            return response

    except json.JSONDecodeError:
        response = Response(
            json.dumps({"error": "Invalid JSON in request body"}), status=400
        )
        response.set_header("Content-Type", "application/json")
        return response
    except Exception as e:
        logger.error(f"Error saving vault config: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def test_vault_connection_handler(request: Request, app) -> Response:
    """Test connection to Vault server."""
    try:
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        # Validate required fields
        if "url" not in data or not data["url"]:
            response = Response(
                json.dumps({"error": "Vault URL is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        if "token" not in data or not data["token"]:
            response = Response(
                json.dumps({"error": "Vault token is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        # Sanitize inputs
        vault_url = sanitize_url(data["url"])
        if not vault_url:
            response = Response(
                json.dumps({"error": "Invalid Vault URL format"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        vault_token = sanitize_string(data["token"], max_length=500)
        vault_namespace = sanitize_string(data.get("namespace", ""), max_length=255) or None
        
        # Test connection
        success, message = test_vault_connection(vault_url, vault_token, vault_namespace)
        
        if success:
            response = Response(
                json.dumps({"success": True, "message": message}), 
                status=200
            )
            response.set_header("Content-Type", "application/json")
            return response
        else:
            response = Response(
                json.dumps({"success": False, "message": message}), 
                status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

    except json.JSONDecodeError:
        response = Response(
            json.dumps({"error": "Invalid JSON in request body"}), status=400
        )
        response.set_header("Content-Type", "application/json")
        return response
    except Exception as e:
        logger.error(f"Error testing vault connection: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def list_secrets_engines_handler(request: Request, app) -> Response:
    """List all secrets engines in Vault."""
    try:
        # Get Vault configuration
        vault_config = get_vault_config()
        if not vault_config:
            response = Response(
                json.dumps({"error": "Vault is not configured"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        vault_url = vault_config.get('url')
        vault_token = vault_config.get('token')
        vault_namespace = vault_config.get('namespace')
        
        if not vault_url or not vault_token:
            response = Response(
                json.dumps({"error": "Vault URL and token are required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        # List secrets engines
        success, result = list_secrets_engines(vault_url, vault_token, vault_namespace)
        
        if success:
            response = Response(
                json.dumps({"engines": result}), 
                status=200
            )
            response.set_header("Content-Type", "application/json")
            return response
        else:
            response = Response(
                json.dumps({"error": result}), 
                status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error listing secrets engines: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def enable_secrets_engine_handler(request: Request, app) -> Response:
    """Enable a secrets engine in Vault."""
    try:
        body = request.body
        if not body:
            response = Response(
                json.dumps({"error": "Request body is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

        data = json.loads(body)
        
        # Validate required fields
        if "engine_type" not in data or not data["engine_type"]:
            response = Response(
                json.dumps({"error": "Engine type is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        if "path" not in data or not data["path"]:
            response = Response(
                json.dumps({"error": "Path is required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        # Get Vault configuration
        vault_config = get_vault_config()
        if not vault_config:
            response = Response(
                json.dumps({"error": "Vault is not configured"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        vault_url = vault_config.get('url')
        vault_token = vault_config.get('token')
        vault_namespace = vault_config.get('namespace')
        
        if not vault_url or not vault_token:
            response = Response(
                json.dumps({"error": "Vault URL and token are required"}), status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        # Sanitize inputs
        engine_type = sanitize_string(data["engine_type"], max_length=50)
        path = sanitize_string(data["path"], max_length=255)
        max_versions = data.get("max_versions")
        
        # Validate engine type
        if engine_type not in ['kv', 'kv-v2']:
            response = Response(
                json.dumps({"error": "Invalid engine type. Must be 'kv' or 'kv-v2'"}), 
                status=400
            )
            response.set_header("Content-Type", "application/json")
            return response
        
        # Validate max_versions if provided
        if max_versions is not None:
            try:
                max_versions = int(max_versions)
                if max_versions < 1 or max_versions > 100:
                    response = Response(
                        json.dumps({"error": "Max versions must be between 1 and 100"}), 
                        status=400
                    )
                    response.set_header("Content-Type", "application/json")
                    return response
            except (ValueError, TypeError):
                response = Response(
                    json.dumps({"error": "Max versions must be a valid number"}), 
                    status=400
                )
                response.set_header("Content-Type", "application/json")
                return response
        
        # Enable secrets engine
        success, message = enable_secrets_engine(
            vault_url, 
            vault_token, 
            engine_type, 
            path, 
            vault_namespace, 
            max_versions
        )
        
        if success:
            response = Response(
                json.dumps({"message": message}), 
                status=200
            )
            response.set_header("Content-Type", "application/json")
            return response
        else:
            response = Response(
                json.dumps({"error": message}), 
                status=400
            )
            response.set_header("Content-Type", "application/json")
            return response

    except json.JSONDecodeError:
        response = Response(
            json.dumps({"error": "Invalid JSON in request body"}), status=400
        )
        response.set_header("Content-Type", "application/json")
        return response
    except Exception as e:
        logger.error(f"Error enabling secrets engine: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


# Context API Handlers
def validate_context_data(data: dict) -> tuple[bool, Optional[str]]:
    """Validate context data."""
    # Check required fields
    if "name" not in data or not data["name"]:
        return False, "Context name is required"

    if "project_id" not in data:
        return False, "Project ID is required"

    # Validate name length
    name = data["name"].strip()
    if len(name) < 1:
        return False, "Context name cannot be empty"
    if len(name) > 255:
        return False, "Context name is too long (max 255 characters)"

    # Validate description length if provided
    if "description" in data and data["description"]:
        if len(data["description"]) > 1000:
            return False, "Description is too long (max 1000 characters)"

    # Validate project_id is an integer
    try:
        int(data["project_id"])
    except (ValueError, TypeError):
        return False, "Invalid project ID"

    return True, None


def create_context_handler(request: Request, app) -> Response:
    """Create a new context."""
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
        is_valid, error_message = validate_context_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Verify project exists
            project_id = int(data["project_id"])
            project = session.get(Project, project_id)
            if not project:
                response = Response(
                    json.dumps({"error": "Project not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Create new context
            context = Context(
                name=sanitize_string(data["name"], max_length=255),
                description=sanitize_string(data.get("description", ""), max_length=1000) or None,
                project_id=project_id,
            )

            session.add(context)
            session.flush()
            session.refresh(context)

            response_body = json.dumps(
                {
                    "id": context.id,
                    "name": context.name,
                    "description": context.description,
                    "project_id": context.project_id,
                    "created_at": context.created_at.isoformat(),
                    "updated_at": context.updated_at.isoformat(),
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
        logger.error(f"Error creating context: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def list_contexts_handler(request: Request, app) -> Response:
    """List all contexts."""
    try:
        with get_session() as session:
            statement = select(Context).order_by(Context.created_at.desc())
            contexts = session.exec(statement).all()

            # Get project names for each context
            contexts_data = []
            for context in contexts:
                project = session.get(Project, context.project_id)
                contexts_data.append({
                    "id": context.id,
                    "name": context.name,
                    "description": context.description,
                    "project_id": context.project_id,
                    "project_name": project.name if project else "Unknown",
                    "created_at": context.created_at.isoformat(),
                    "updated_at": context.updated_at.isoformat(),
                })

            response_body = json.dumps({"contexts": contexts_data})
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error listing contexts: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def get_context_handler(request: Request, app, context_id: str) -> Response:
    """Get a single context by ID."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            context = session.get(Context, cid)

            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Get project name
            project = session.get(Project, context.project_id)

            response_body = json.dumps(
                {
                    "id": context.id,
                    "name": context.name,
                    "description": context.description,
                    "project_id": context.project_id,
                    "project_name": project.name if project else "Unknown",
                    "created_at": context.created_at.isoformat(),
                    "updated_at": context.updated_at.isoformat(),
                }
            )
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error getting context: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def update_context_handler(request: Request, app, context_id: str) -> Response:
    """Update a context."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
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
        is_valid, error_message = validate_context_data(data)
        if not is_valid:
            response = Response(json.dumps({"error": error_message}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            context = session.get(Context, cid)

            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Verify project exists if changing project
            project_id = int(data["project_id"])
            project = session.get(Project, project_id)
            if not project:
                response = Response(
                    json.dumps({"error": "Project not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Update fields
            context.name = sanitize_string(data["name"], max_length=255)
            context.description = (
                sanitize_string(data.get("description", ""), max_length=1000) or None
            )
            context.project_id = project_id
            context.updated_at = datetime.utcnow()

            session.add(context)
            session.flush()
            session.refresh(context)

            response_body = json.dumps(
                {
                    "id": context.id,
                    "name": context.name,
                    "description": context.description,
                    "project_id": context.project_id,
                    "project_name": project.name,
                    "created_at": context.created_at.isoformat(),
                    "updated_at": context.updated_at.isoformat(),
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
        logger.error(f"Error updating context: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_context_handler(request: Request, app, context_id: str) -> Response:
    """Delete a context."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            context = session.get(Context, cid)

            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # CASCADE will handle deleting associated secrets automatically
            session.delete(context)

            response = Response(
                json.dumps({"message": "Context deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error deleting context: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


# Context Secret API Handlers
def list_context_secrets_handler(request: Request, app, context_id: str) -> Response:
    """List all secrets for a context."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Verify context exists
            context = session.get(Context, cid)
            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Get all secrets for this context
            statement = select(ContextSecret).where(ContextSecret.context_id == cid).order_by(ContextSecret.created_at.desc())
            secrets = session.exec(statement).all()

            secrets_data = [
                {
                    "id": secret.id,
                    "context_id": secret.context_id,
                    "env_var_name": secret.env_var_name,
                    "secret_key": secret.secret_key,
                    "vault_path": secret.vault_path,
                    "created_at": secret.created_at.isoformat(),
                    "updated_at": secret.updated_at.isoformat(),
                }
                for secret in secrets
            ]

            response_body = json.dumps({"secrets": secrets_data})
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error listing context secrets: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def add_context_secret_handler(request: Request, app, context_id: str) -> Response:
    """Add a secret to a context."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
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

        # Validate required fields
        if "env_var_name" not in data or not data["env_var_name"]:
            response = Response(json.dumps({"error": "Environment variable name is required"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        if "secret_key" not in data or not data["secret_key"]:
            response = Response(json.dumps({"error": "Secret key is required"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        if "vault_path" not in data or not data["vault_path"]:
            response = Response(json.dumps({"error": "Vault path is required"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        env_var_name = sanitize_string(data["env_var_name"], max_length=255)
        secret_key = sanitize_string(data["secret_key"], max_length=255)
        vault_path = sanitize_string(data["vault_path"], max_length=500)

        if len(env_var_name) < 1:
            response = Response(json.dumps({"error": "Environment variable name cannot be empty"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        if len(secret_key) < 1:
            response = Response(json.dumps({"error": "Secret key cannot be empty"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        if len(vault_path) < 1:
            response = Response(json.dumps({"error": "Vault path cannot be empty"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Verify context exists
            context = session.get(Context, cid)
            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Check if env_var_name already exists for this context
            statement = select(ContextSecret).where(
                ContextSecret.context_id == cid,
                ContextSecret.env_var_name == env_var_name
            )
            existing = session.exec(statement).first()
            if existing:
                response = Response(
                    json.dumps({"error": "Environment variable name already exists for this context"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Create new context secret
            context_secret = ContextSecret(
                context_id=cid,
                env_var_name=env_var_name,
                secret_key=secret_key,
                vault_path=vault_path,
            )

            session.add(context_secret)
            session.flush()
            session.refresh(context_secret)

            response_body = json.dumps(
                {
                    "id": context_secret.id,
                    "context_id": context_secret.context_id,
                    "env_var_name": context_secret.env_var_name,
                    "secret_key": context_secret.secret_key,
                    "vault_path": context_secret.vault_path,
                    "created_at": context_secret.created_at.isoformat(),
                    "updated_at": context_secret.updated_at.isoformat(),
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
        logger.error(f"Error adding context secret: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_context_secret_handler(request: Request, app, context_id: str, secret_id: str) -> Response:
    """Delete a secret from a context."""
    try:
        # Validate IDs are integers
        try:
            cid = int(context_id)
            sid = int(secret_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Get the secret
            secret = session.get(ContextSecret, sid)

            if not secret:
                response = Response(
                    json.dumps({"error": "Secret not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Verify the secret belongs to the specified context
            if secret.context_id != cid:
                response = Response(
                    json.dumps({"error": "Secret does not belong to this context"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            session.delete(secret)

            response = Response(
                json.dumps({"message": "Secret deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error deleting context secret: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


# Context Environment Variable API Handlers
def list_context_env_vars_handler(request: Request, app, context_id: str) -> Response:
    """List all environment variables for a context."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Verify context exists
            context = session.get(Context, cid)
            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Get all env vars for this context
            statement = select(ContextEnvVar).where(ContextEnvVar.context_id == cid).order_by(ContextEnvVar.created_at.desc())
            env_vars = session.exec(statement).all()

            env_vars_data = [
                {
                    "id": env_var.id,
                    "context_id": env_var.context_id,
                    "key": env_var.key,
                    "value": env_var.value,
                    "created_at": env_var.created_at.isoformat(),
                    "updated_at": env_var.updated_at.isoformat(),
                }
                for env_var in env_vars
            ]

            response_body = json.dumps({"env_vars": env_vars_data})
            response = Response(response_body, status=200)
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error listing context env vars: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def add_context_env_var_handler(request: Request, app, context_id: str) -> Response:
    """Add an environment variable to a context."""
    try:
        # Validate context_id is an integer
        try:
            cid = int(context_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid context ID"}), status=400)
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

        # Validate required fields
        if "key" not in data or not data["key"]:
            response = Response(json.dumps({"error": "Key is required"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        if "value" not in data or not data["value"]:
            response = Response(json.dumps({"error": "Value is required"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        key = sanitize_string(data["key"], max_length=255)
        value = sanitize_string(data["value"], max_length=1000)

        if len(key) < 1:
            response = Response(json.dumps({"error": "Key cannot be empty"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        if len(value) < 1:
            response = Response(json.dumps({"error": "Value cannot be empty"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Verify context exists
            context = session.get(Context, cid)
            if not context:
                response = Response(
                    json.dumps({"error": "Context not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Check if key already exists for this context
            statement = select(ContextEnvVar).where(
                ContextEnvVar.context_id == cid,
                ContextEnvVar.key == key
            )
            existing = session.exec(statement).first()
            if existing:
                response = Response(
                    json.dumps({"error": "Environment variable key already exists for this context"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Create new context env var
            context_env_var = ContextEnvVar(
                context_id=cid,
                key=key,
                value=value,
            )

            session.add(context_env_var)
            session.flush()
            session.refresh(context_env_var)

            response_body = json.dumps(
                {
                    "id": context_env_var.id,
                    "context_id": context_env_var.context_id,
                    "key": context_env_var.key,
                    "value": context_env_var.value,
                    "created_at": context_env_var.created_at.isoformat(),
                    "updated_at": context_env_var.updated_at.isoformat(),
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
        logger.error(f"Error adding context env var: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response


def delete_context_env_var_handler(request: Request, app, context_id: str, env_var_id: str) -> Response:
    """Delete an environment variable from a context."""
    try:
        # Validate IDs are integers
        try:
            cid = int(context_id)
            eid = int(env_var_id)
        except ValueError:
            response = Response(json.dumps({"error": "Invalid ID"}), status=400)
            response.set_header("Content-Type", "application/json")
            return response

        with get_session() as session:
            # Get the env var
            env_var = session.get(ContextEnvVar, eid)

            if not env_var:
                response = Response(
                    json.dumps({"error": "Environment variable not found"}), status=404
                )
                response.set_header("Content-Type", "application/json")
                return response

            # Verify the env var belongs to the specified context
            if env_var.context_id != cid:
                response = Response(
                    json.dumps({"error": "Environment variable does not belong to this context"}), status=400
                )
                response.set_header("Content-Type", "application/json")
                return response

            session.delete(env_var)

            response = Response(
                json.dumps({"message": "Environment variable deleted successfully"}), status=200
            )
            response.set_header("Content-Type", "application/json")
            return response

    except Exception as e:
        logger.error(f"Error deleting context env var: {e}", exc_info=True)
        response = Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}), status=500
        )
        response.set_header("Content-Type", "application/json")
        return response
