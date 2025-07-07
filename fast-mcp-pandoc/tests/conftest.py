"""
Test configuration and fixtures for fast-mcp-pandoc.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator

import pytest
from fastapi.testclient import TestClient

from fast_mcp_pandoc.server import app


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """Create a FastAPI test client."""
    return TestClient(app)


@pytest.fixture(scope="session")
def test_markdown_content() -> str:
    """Test markdown content for conversion tests."""
    return """# Test Document
    
This is a **test document** with some _formatting_.

## Section 1

* Item 1
* Item 2

## Section 2

1. First
2. Second
"""


@pytest.fixture(scope="function")
def temp_file_path() -> Generator[str, None, None]:
    """Create a temporary file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        yield path
    finally:
        os.close(fd)
        if os.path.exists(path):
            os.unlink(path)


@pytest.fixture(scope="function")
def temp_output_path() -> Generator[str, None, None]:
    """Create a temporary output path for files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield os.path.join(temp_dir, "output.pdf")
