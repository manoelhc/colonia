"""RabbitMQ connection and messaging utilities."""

import os
import json
import logging
import pika
from typing import Optional

# Get logger without configuring it at module level
logger = logging.getLogger(__name__)


def get_rabbitmq_connection() -> pika.BlockingConnection:
    """Create and return a RabbitMQ connection."""
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "colonia")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "colonia")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
    )

    return pika.BlockingConnection(parameters)


def send_project_scan_message(project_id: int, project_name: str, repository_url: Optional[str]) -> bool:
    """Send a message to RabbitMQ to trigger a repo scan."""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # Declare the queue (idempotent operation)
        channel.queue_declare(queue="repo-scan", durable=True)

        # Prepare message
        message = {
            "project_id": project_id,
            "project_name": project_name,
            "repository_url": repository_url,
        }

        # Send message
        channel.basic_publish(
            exchange="",
            routing_key="repo-scan",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )

        connection.close()
        logger.info(f"Sent repo scan message for project {project_id}")
        return True

    except Exception as e:
        logger.error(f"Error sending message to RabbitMQ for project {project_id}: {e}", exc_info=True)
        return False
