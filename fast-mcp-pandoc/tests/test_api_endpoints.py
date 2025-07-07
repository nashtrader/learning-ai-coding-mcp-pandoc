"""
Test suite for Fast-MCP-Pandoc API endpoints.
"""

import json
import os
import time
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient) -> None:
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_heartbeat_endpoint(test_client: TestClient) -> None:
    """Test the heartbeat endpoint."""
    response = test_client.get("/heartbeat")
    assert response.status_code == 200
    assert response.json() == {"alive": True}


def test_convert_endpoint_content_to_html(test_client: TestClient, test_markdown_content: str) -> None:
    """Test converting markdown content to HTML."""
    response = test_client.post(
        "/convert",
        json={
            "contents": test_markdown_content,
            "input_format": "markdown",
            "output_format": "html"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "<h1" in data["result"]  # Check for HTML tags
    assert "Test Document" in data["result"]


def test_convert_endpoint_validation_errors(test_client: TestClient) -> None:
    """Test validation errors in the convert endpoint."""
    # Test missing content source
    response = test_client.post(
        "/convert",
        json={
            "input_format": "markdown",
            "output_format": "html"
        }
    )
    assert response.status_code == 422  # Validation error
    
    # Test unsupported format
    response = test_client.post(
        "/convert",
        json={
            "contents": "# Test",
            "input_format": "unsupported",
            "output_format": "html"
        }
    )
    assert response.status_code == 422  # Validation error
    
    # Test missing output_file for advanced formats
    response = test_client.post(
        "/convert",
        json={
            "contents": "# Test",
            "input_format": "markdown",
            "output_format": "pdf"
        }
    )
    assert response.status_code == 422  # Validation error


def test_convert_endpoint_file_to_file(
    test_client: TestClient, 
    test_markdown_content: str,
    temp_file_path: str,
    temp_output_path: str
) -> None:
    """Test converting from a file to another file."""
    # Write test content to input file
    with open(temp_file_path, "w") as f:
        f.write(test_markdown_content)
    
    # Test conversion
    response = test_client.post(
        "/convert",
        json={
            "input_file": temp_file_path,
            "input_format": "markdown",
            "output_format": "html",
            "output_file": temp_output_path.replace(".pdf", ".html")
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert os.path.exists(temp_output_path.replace(".pdf", ".html"))


def test_convert_stream_endpoint(test_client: TestClient, test_markdown_content: str) -> None:
    """Test the streaming conversion endpoint."""
    response = test_client.get(
        "/convert/stream",
        params={
            "contents": test_markdown_content,
            "input_format": "markdown",
            "output_format": "html"
        },
        stream=True
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    
    # Collect events
    events = []
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)
                
                # If we got a complete or error event, we can stop
                if event_data.get("event") in ["complete", "error"]:
                    break
    
    # Verify we got at least a progress and a complete event
    progress_events = [e for e in events if e.get("event") == "progress"]
    complete_events = [e for e in events if e.get("event") == "complete"]
    
    assert len(progress_events) > 0, "Should have at least one progress event"
    assert len(complete_events) > 0, "Should have a complete event"
    
    # Check completion data contains HTML result
    assert "<h1" in complete_events[0]["data"]["result"]
