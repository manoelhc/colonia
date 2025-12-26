#!/usr/bin/env python3
"""RabbitMQ consumer for scanning repository colonia.yaml files."""

import json
import os
import sys
import logging
import pika
import yaml
import requests
from typing import Optional, Dict, Any, List
from sqlmodel import select, delete

# Add parent directory to path to import from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Project, Environment, Stack, StackEnvironment
from app.database import get_session

# Get logger without configuring it at module level
logger = logging.getLogger(__name__)


def fetch_colonia_yaml(repository_url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch colonia.yaml from a repository.
    
    Supports GitHub repositories by converting the URL to raw content URL.
    For example: https://github.com/user/repo -> https://raw.githubusercontent.com/user/repo/main/colonia.yaml
    """
    if not repository_url:
        return None

    try:
        # Convert GitHub URL to raw content URL
        # Ensure github.com is the actual domain
        if repository_url.startswith("https://github.com/") or repository_url.startswith("http://github.com/"):
            # Extract user and repo from URL
            # Handle various formats: https://github.com/user/repo or https://github.com/user/repo.git
            parts = repository_url.rstrip('/').rstrip('.git').split('github.com/')
            if len(parts) == 2:
                repo_path = parts[1]
                # Try main branch first, then master
                for branch in ['main', 'master']:
                    raw_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/colonia.yaml"
                    response = requests.get(raw_url, timeout=10, verify=True)
                    if response.status_code == 200:
                        return yaml.safe_load(response.text)
        
        # For other repository types, this would need to be extended
        logger.warning(f"Could not fetch colonia.yaml from {repository_url}")
        return None

    except requests.RequestException as e:
        logger.error(f"Error fetching colonia.yaml: {e}", exc_info=True)
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing colonia.yaml: {e}", exc_info=True)
        return None


def process_colonia_yaml(project_id: int, colonia_config: Optional[Dict[str, Any]]) -> None:
    """
    Process colonia.yaml and create/update/delete resources.
    
    Args:
        project_id: The project ID to associate resources with
        colonia_config: Parsed colonia.yaml content, or None if file doesn't exist
    """
    with get_session() as session:
        # If no config, delete all existing resources for this project
        if not colonia_config:
            logger.info(f"No colonia.yaml found for project {project_id}, cleaning up existing resources")
            
            # Delete stack-environment relationships
            session.exec(
                delete(StackEnvironment).where(
                    StackEnvironment.stack_id.in_(
                        select(Stack.id).where(Stack.project_id == project_id)
                    )
                )
            )
            
            # Delete stacks
            session.exec(delete(Stack).where(Stack.project_id == project_id))
            
            # Delete environments
            session.exec(delete(Environment).where(Environment.project_id == project_id))
            
            logger.info(f"Cleaned up resources for project {project_id}")
            return

        # Process environments
        environments_config = colonia_config.get('environments', [])
        existing_envs = session.exec(
            select(Environment).where(Environment.project_id == project_id)
        ).all()
        
        # Create a map of existing environments by name
        existing_envs_map = {env.name: env for env in existing_envs}
        config_env_names = set()

        for env_config in environments_config:
            env_name = env_config.get('name')
            env_dir = env_config.get('dir')
            
            if not env_name or not env_dir:
                logger.warning(f"Skipping invalid environment config: {env_config}")
                continue
                
            config_env_names.add(env_name)
            
            if env_name in existing_envs_map:
                # Update existing environment
                env = existing_envs_map[env_name]
                env.directory = env_dir
                session.add(env)
                logger.info(f"Updated environment: {env_name}")
            else:
                # Create new environment
                env = Environment(
                    project_id=project_id,
                    name=env_name,
                    directory=env_dir
                )
                session.add(env)
                logger.info(f"Created environment: {env_name}")
        
        session.flush()
        
        # Delete environments that are no longer in the config
        for env_name, env in existing_envs_map.items():
            if env_name not in config_env_names:
                # Delete stack-environment relationships first
                session.exec(
                    delete(StackEnvironment).where(StackEnvironment.environment_id == env.id)
                )
                session.delete(env)
                logger.info(f"Deleted environment: {env_name}")

        # Refresh environment list after changes
        all_envs = session.exec(
            select(Environment).where(Environment.project_id == project_id)
        ).all()
        env_name_to_id = {env.name: env.id for env in all_envs}

        # Process stacks
        stacks_config = colonia_config.get('stacks', [])
        existing_stacks = session.exec(
            select(Stack).where(Stack.project_id == project_id)
        ).all()
        
        # Create a map of existing stacks by name
        existing_stacks_map = {stack.name: stack for stack in existing_stacks}
        config_stack_names = set()

        for stack_config in stacks_config:
            stack_name = stack_config.get('name')
            stack_path = stack_config.get('stack')
            stack_envs = stack_config.get('environments', [])
            
            if not stack_name or not stack_path:
                logger.warning(f"Skipping invalid stack config: {stack_config}")
                continue
                
            config_stack_names.add(stack_name)
            
            if stack_name in existing_stacks_map:
                # Update existing stack
                stack = existing_stacks_map[stack_name]
                stack.stack_path = stack_path
                session.add(stack)
                logger.info(f"Updated stack: {stack_name}")
            else:
                # Create new stack
                stack = Stack(
                    project_id=project_id,
                    name=stack_name,
                    stack_path=stack_path
                )
                session.add(stack)
                session.flush()
                session.refresh(stack)
                logger.info(f"Created stack: {stack_name}")
            
            # Update stack-environment relationships
            # First, delete existing relationships for this stack
            session.exec(
                delete(StackEnvironment).where(StackEnvironment.stack_id == stack.id)
            )
            
            # Then create new relationships
            for env_name in stack_envs:
                if env_name in env_name_to_id:
                    stack_env = StackEnvironment(
                        stack_id=stack.id,
                        environment_id=env_name_to_id[env_name]
                    )
                    session.add(stack_env)
                    logger.info(f"Linked stack '{stack_name}' to environment '{env_name}'")
                else:
                    logger.warning(f"Environment '{env_name}' not found for stack '{stack_name}'")
        
        # Delete stacks that are no longer in the config
        for stack_name, stack in existing_stacks_map.items():
            if stack_name not in config_stack_names:
                # Delete stack-environment relationships first
                session.exec(
                    delete(StackEnvironment).where(StackEnvironment.stack_id == stack.id)
                )
                session.delete(stack)
                logger.info(f"Deleted stack: {stack_name}")

        logger.info(f"Successfully processed colonia.yaml for project {project_id}")


def callback(ch, method, properties, body):
    """Callback function to process messages from RabbitMQ."""
    try:
        # Parse message
        message = json.loads(body)
        project_id = message.get('project_id')
        project_name = message.get('project_name')
        repository_url = message.get('repository_url')

        logger.info(f"Processing repo scan for project: {project_name} (ID: {project_id})")
        
        # Fetch colonia.yaml
        colonia_config = fetch_colonia_yaml(repository_url)
        
        # Process the configuration
        process_colonia_yaml(project_id, colonia_config)
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Completed processing for project {project_id}")

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in message: {e}", exc_info=True)
        # Reject malformed messages without requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        # Reject message without requeue for permanent errors
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    """Main function to start the RabbitMQ consumer."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "colonia")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "colonia")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
    )

    logger.info(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}...")

    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare the queue (idempotent operation)
        channel.queue_declare(queue="repo-scan", durable=True)

        # Set prefetch count to 1 to process one message at a time
        channel.basic_qos(prefetch_count=1)

        # Start consuming
        channel.basic_consume(queue="repo-scan", on_message_callback=callback)

        logger.info("Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
