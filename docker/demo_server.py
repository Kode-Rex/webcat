# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Demo server for WebCat with FastAPI + FastMCP integration and SSE streaming."""

import asyncio
import logging
import os
import tempfile
import threading
import time

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastmcp import FastMCP

from api_tools import create_webcat_functions, setup_webcat_tools
from demo_utils import (
    format_sse_message,
    get_server_info,
    handle_health_operation,
    handle_search_operation,
)
from health import setup_health_endpoints

# Load environment variables
load_dotenv()

# Set up logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.environ.get("LOG_DIR", tempfile.gettempdir())
LOG_FILE = os.path.join(LOG_DIR, "webcat_demo.log")

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create formatters
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Setup console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Setup rotating file handler
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.info("Demo server logging initialized")


async def _generate_webcat_stream(
    webcat_functions, operation: str, query: str, max_results: int
):
    """Generate SSE stream for WebCat operations.

    Args:
        webcat_functions: Dictionary of WebCat functions
        operation: Operation to perform
        query: Search query
        max_results: Maximum results

    Yields:
        SSE formatted messages
    """
    try:
        # Send connection message
        yield format_sse_message(
            "connection",
            status="connected",
            message="WebCat stream started",
            operation=operation,
        )

        if operation == "search" and query:
            search_func = webcat_functions.get("search")
            if search_func:
                async for msg in handle_search_operation(
                    search_func, query, max_results
                ):
                    yield msg
            else:
                yield format_sse_message(
                    "error", message="Search function not available"
                )

        elif operation == "health":
            health_func = webcat_functions.get("health_check")
            async for msg in handle_health_operation(health_func):
                yield msg

        else:
            # Just connection - send server info
            yield format_sse_message("data", data=get_server_info())
            yield format_sse_message("complete", message="Connection established")

        # Keep alive with heartbeat
        heartbeat_count = 0
        while True:
            await asyncio.sleep(30)
            heartbeat_count += 1
            yield format_sse_message(
                "heartbeat", timestamp=time.time(), count=heartbeat_count
            )

    except Exception as e:
        logger.error(f"Error in SSE stream: {str(e)}")
        yield format_sse_message("error", message=str(e))


async def run_server():
    """Create and configure the FastAPI app with SSE support."""

    # Create FastAPI app with CORS middleware
    app = FastAPI(
        title="WebCat MCP Demo Server",
        description="WebCat server with FastMCP integration and SSE streaming demo",
        version="2.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Setup health endpoints
    setup_health_endpoints(app)

    # Initialize FastMCP server
    mcp_server = FastMCP("WebCat Demo Server")

    # Setup WebCat tools
    webcat_functions = create_webcat_functions()
    setup_webcat_tools(mcp_server, webcat_functions)

    # Add custom SSE endpoint for demo
    @app.get("/sse")
    async def webcat_stream(
        operation: str = Query(
            "connect", description="Operation to perform: connect, search, health"
        ),
        query: str = Query("", description="Search query for search operations"),
        max_results: int = Query(5, description="Maximum number of search results"),
    ):
        """Stream WebCat functionality via SSE"""
        return StreamingResponse(
            _generate_webcat_stream(webcat_functions, operation, query, max_results),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    # Mount FastMCP server at /mcp
    mcp_app = mcp_server.sse_app()
    app.mount("/mcp", mcp_app)

    logger.info("FastAPI app configured with SSE and FastMCP integration")
    return app


def run_demo_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the WebCat demo server with SSE endpoints and health checks."""

    def run_health_server():
        """Run the health server on port + 1."""
        from health import create_health_app

        health_app = create_health_app()
        health_port = port + 1
        logger.info(f"Starting health server on port {health_port}")
        uvicorn.run(health_app, host=host, port=health_port, log_level="warning")

    # Start health server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Initialize main app
    app = asyncio.run(run_server())

    # Log endpoints
    logger.info(f"WebCat Demo Server: http://{host}:{port}")
    logger.info(f"SSE Demo Endpoint: http://{host}:{port}/sse")
    logger.info(f"FastMCP Endpoint: http://{host}:{port}/mcp")
    logger.info(f"Health endpoints: http://{host}:{port + 1}/health")
    logger.info(f"Demo Client: http://{host}:{port + 1}/demo")

    print("\n🐱 WebCat MCP Demo Server Starting...")
    print(f"📡 Main Server: http://{host}:{port}")
    print(f"🔗 SSE Demo: http://{host}:{port}/sse")
    print(f"🛠️ FastMCP: http://{host}:{port}/mcp")
    print(f"💗 Health: http://{host}:{port + 1}/health")
    print(f"🎨 Demo UI: http://{host}:{port + 1}/demo")
    print(f"📊 Server Status: http://{host}:{port + 1}/status")
    print("\n✨ Ready for connections!")

    # Run main server
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_demo_server(port=port)
