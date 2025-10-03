# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health endpoints module for WebCat MCP server."""

import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)


def _get_health_status() -> dict:
    """Get server health status.

    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "service": "webcat-mcp",
        "timestamp": time.time(),
        "version": "2.2.0",
        "uptime": "running",
    }


def _get_unhealthy_status(error: str) -> dict:
    """Get unhealthy status response.

    Args:
        error: Error message

    Returns:
        Unhealthy status dictionary
    """
    return {
        "status": "unhealthy",
        "error": error,
        "timestamp": time.time(),
    }


def _client_not_found_response(client_path: Path) -> JSONResponse:
    """Create response for missing client file.

    Args:
        client_path: Path where client was expected

    Returns:
        JSONResponse with 404 status
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "WebCat client file not found",
            "expected_path": str(client_path),
            "exists": False,
        },
    )


def _client_error_response(error: str) -> JSONResponse:
    """Create response for client loading error.

    Args:
        error: Error message

    Returns:
        JSONResponse with 500 status
    """
    return JSONResponse(
        status_code=500,
        content={"error": "Failed to serve WebCat client", "details": error},
    )


def _load_client_file(client_path: Path) -> HTMLResponse:
    """Load and return client HTML file.

    Args:
        client_path: Path to client HTML file

    Returns:
        HTMLResponse with client content
    """
    html_content = client_path.read_text(encoding="utf-8")
    logger.info("Successfully loaded WebCat demo client")
    return HTMLResponse(content=html_content)


def _get_server_configuration() -> dict:
    """Get server configuration dictionary.

    Returns:
        Configuration dictionary
    """
    return {
        "serper_api_configured": bool(os.environ.get("SERPER_API_KEY")),
        "port": int(os.environ.get("PORT", 8000)),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        "log_dir": os.environ.get("LOG_DIR", "/tmp"),
    }


def _get_server_endpoints() -> dict:
    """Get server endpoints dictionary.

    Returns:
        Endpoints dictionary
    """
    return {
        "main_mcp": "/mcp",
        "sse_demo": "/sse",
        "health": "/health",
        "status": "/status",
        "demo_client": "/demo",
    }


def _get_server_capabilities() -> list:
    """Get server capabilities list.

    Returns:
        List of capabilities
    """
    return [
        "Web search with Serper API",
        "DuckDuckGo fallback search",
        "Content extraction and scraping",
        "Markdown conversion",
        "FastMCP protocol support",
        "SSE streaming",
        "Demo UI client",
    ]


def _get_detailed_status() -> dict:
    """Get detailed server status.

    Returns:
        Status dictionary
    """
    return {
        "service": "WebCat MCP Server",
        "status": "running",
        "version": "2.2.0",
        "timestamp": time.time(),
        "configuration": _get_server_configuration(),
        "endpoints": _get_server_endpoints(),
        "capabilities": _get_server_capabilities(),
    }


def _get_status_error(error: str) -> dict:
    """Get status error response.

    Args:
        error: Error message

    Returns:
        Error dictionary
    """
    return {
        "error": "Failed to get server status",
        "details": error,
        "timestamp": time.time(),
    }


def _get_root_info() -> dict:
    """Get root endpoint information.

    Returns:
        Root information dictionary
    """
    return {
        "service": "WebCat MCP Server",
        "version": "2.2.0",
        "description": "Web search and content extraction with MCP protocol support",
        "endpoints": {
            "demo_client": "/demo",
            "health": "/health",
            "status": "/status",
            "mcp_sse": "/mcp",
        },
        "documentation": "Access /demo for the demo interface",
    }


def setup_health_endpoints(app: FastAPI):
    """Setup health and utility endpoints for the WebCat server."""

    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        try:
            return _get_health_status()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(status_code=500, content=_get_unhealthy_status(str(e)))

    @app.get("/demo")
    async def sse_client():
        """Serve the WebCat SSE demo client."""
        try:
            current_dir = Path(__file__).parent
            client_path = current_dir.parent / "examples" / "webcat_client.html"
            logger.info(f"Looking for client file at: {client_path}")

            if client_path.exists():
                return _load_client_file(client_path)

            logger.error(f"WebCat client file not found at: {client_path}")
            return _client_not_found_response(client_path)
        except Exception as e:
            logger.error(f"Failed to serve WebCat client: {str(e)}")
            return _client_error_response(str(e))

    @app.get("/status")
    async def server_status():
        """Detailed server status endpoint."""
        try:
            return _get_detailed_status()
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return JSONResponse(status_code=500, content=_get_status_error(str(e)))

    @app.get("/")
    async def root():
        """Root endpoint with basic information."""
        return _get_root_info()


def create_health_app() -> FastAPI:
    """Create a separate FastAPI app for health endpoints."""
    app = FastAPI(
        title="WebCat MCP Health Service",
        description="Health monitoring and demo client for WebCat MCP server",
        version="2.2.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    setup_health_endpoints(app)
    return app


def create_demo_app() -> FastAPI:
    """Create the main demo app with both health and SSE endpoints."""
    app = FastAPI(
        title="WebCat MCP Demo Server",
        description="Complete WebCat MCP server with demo UI and SSE streaming",
        version="2.2.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    setup_health_endpoints(app)
    return app
