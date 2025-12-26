"""Tests for RabbitMQ functionality."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from app.rabbitmq import send_project_scan_message


@patch('app.rabbitmq.get_rabbitmq_connection')
def test_send_project_scan_message_success(mock_connection):
    """Test successful message sending to RabbitMQ."""
    # Setup mocks
    mock_channel = MagicMock()
    mock_conn = MagicMock()
    mock_conn.channel.return_value = mock_channel
    mock_connection.return_value = mock_conn

    # Call function
    result = send_project_scan_message(
        project_id=1,
        project_name="Test Project",
        repository_url="https://github.com/user/repo"
    )

    # Assertions
    assert result is True
    mock_channel.queue_declare.assert_called_once_with(queue="repo-scan", durable=True)
    mock_channel.basic_publish.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('app.rabbitmq.get_rabbitmq_connection')
def test_send_project_scan_message_failure(mock_connection):
    """Test handling of RabbitMQ connection failure."""
    # Setup mock to raise exception
    mock_connection.side_effect = Exception("Connection failed")

    # Call function
    result = send_project_scan_message(
        project_id=1,
        project_name="Test Project",
        repository_url="https://github.com/user/repo"
    )

    # Assertions
    assert result is False
