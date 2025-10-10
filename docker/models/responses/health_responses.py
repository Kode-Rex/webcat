# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health response models and formatters."""

import os
import time

from constants import CAPABILITIES, SERVICE_NAME, VERSION


def get_health_status() -> dict:
    """Get server health status."""
    return {
        "status": "healthy",
        "service": "webcat-mcp",
        "timestamp": time.time(),
        "version": VERSION,
        "uptime": "running",
    }


def get_unhealthy_status(error: str) -> dict:
    """Get unhealthy status response."""
    return {
        "status": "unhealthy",
        "error": error,
        "timestamp": time.time(),
    }


def get_server_configuration() -> dict:
    """Get server configuration dictionary."""
    return {
        "serper_api_configured": bool(os.environ.get("SERPER_API_KEY")),
        "port": int(os.environ.get("PORT", 8000)),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        "log_dir": os.environ.get("LOG_DIR", "/tmp"),
    }


def get_server_endpoints() -> dict:
    """Get server endpoints dictionary."""
    return {
        "mcp": "/mcp",
        "health": "/health",
        "status": "/status",
    }


def get_detailed_status() -> dict:
    """Get detailed server status."""
    return {
        "service": SERVICE_NAME,
        "status": "running",
        "version": VERSION,
        "timestamp": time.time(),
        "configuration": get_server_configuration(),
        "endpoints": get_server_endpoints(),
        "capabilities": CAPABILITIES,
    }


def get_status_error(error: str) -> dict:
    """Get status error response."""
    return {
        "error": "Failed to get server status",
        "details": error,
        "timestamp": time.time(),
    }


def get_root_info() -> dict:
    """Get root endpoint information."""
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "description": "Web search and content extraction with MCP protocol support",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "status": "/status",
        },
        "documentation": "MCP server - connect via SSE at /mcp/sse endpoint",
    }
