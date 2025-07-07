"""
Data models for the Fast MCP Pandoc API.

This module defines the request and response models for the API endpoints,
including MCP (Model Context Protocol) specific models.
"""

import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class ConversionRequest(BaseModel):
    """Request model for conversion with either content or input_file."""
    contents: Optional[str] = Field(None, description="The content to be converted")
    input_file: Optional[str] = Field(None, description="Path to the input file")
    input_format: str = Field("markdown", description="Source format of the content")
    output_format: str = Field("markdown", description="Desired output format")
    output_file: Optional[str] = Field(None, description="Path where to save the output")

    @validator("input_format", "output_format")
    def validate_formats(cls, v: str) -> str:
        """Validate that the formats are supported."""
        supported_formats = {"markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt"}
        if v.lower() not in supported_formats:
            raise ValueError(f"Format '{v}' not supported. Supported formats: {', '.join(supported_formats)}")
        return v.lower()

    @validator("contents", "input_file")
    def validate_content_sources(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate that at least one of contents or input_file is provided."""
        if "contents" in values and values["contents"] is None and "input_file" in values and values["input_file"] is None:
            raise ValueError("Either 'contents' or 'input_file' must be provided")
        return v

    @validator("output_file", always=True)
    def validate_output_file(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate that output_file is provided for advanced formats."""
        if "output_format" in values:
            advanced_formats = {"pdf", "docx", "rst", "latex", "epub"}
            if values["output_format"] in advanced_formats and not v:
                raise ValueError(f"output_file is required for {values['output_format']} format")
        return v


class ConversionEvent(BaseModel):
    """Base model for SSE events."""
    event: str
    data: Dict[str, Any]


class ConversionProgress(ConversionEvent):
    """Model for conversion progress updates."""
    event: str = "progress"
    data: Dict[str, Any]


class ConversionError(ConversionEvent):
    """Model for conversion errors."""
    event: str = "error"
    data: Dict[str, str]


class ConversionComplete(ConversionEvent):
    """Model for conversion completion notification."""
    event: str = "complete"
    data: Dict[str, Any]


class ConversionHeartbeat(ConversionEvent):
    """Model for heartbeat events to keep the connection alive."""
    event: str = "heartbeat"
    data: Dict[str, Any] = Field(default_factory=lambda: {"timestamp": ""})


# MCP Protocol Models
class MCPToolParameter(BaseModel):
    """Model for a parameter of an MCP tool."""
    name: str
    description: str
    type: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


class MCPTool(BaseModel):
    """Model for an MCP tool description."""
    name: str
    description: str
    parameters: List[MCPToolParameter]


class MCPToolInvocation(BaseModel):
    """Model for an MCP tool invocation."""
    tool: str
    parameters: Dict[str, Any]


class MCPErrorDetail(BaseModel):
    """Model for MCP error details."""
    message: str
    code: Optional[str] = None
    stack: Optional[str] = None


class MCPStatus(str, Enum):
    """Enum for MCP event status."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class MCPEvent(BaseModel):
    """Base model for MCP protocol events."""
    id: str
    status: MCPStatus
    tool: str
    created_at: str
    output: Optional[Any] = None
    error: Optional[MCPErrorDetail] = None
    runtime: Optional[float] = None


class MCPToolsDiscovery(BaseModel):
    """Model for MCP tools discovery response."""
    tools: List[MCPTool]
