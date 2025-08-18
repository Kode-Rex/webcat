#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Simplified demo server that combines health and SSE endpoints in one FastAPI app."""

import asyncio
import json
import logging
import os
import tempfile
import time

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastmcp import FastMCP

from api_tools import create_webcat_functions, setup_webcat_tools

# Import our modules
from health import setup_health_endpoints

# Load environment variables
load_dotenv()

# Set up logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.environ.get("LOG_DIR", tempfile.gettempdir())
LOG_FILE = os.path.join(LOG_DIR, "webcat_simple_demo.log")

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))


def create_demo_app():
    """Create a single FastAPI app with all endpoints."""

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

    # Setup health endpoints (this adds /health, /client, /status, /)
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

        async def generate_webcat_stream():
            try:
                # Send connection message
                yield f"data: {json.dumps({'type': 'connection', 'status': 'connected', 'message': 'WebCat stream started', 'operation': operation})}\n\n"

                if operation == "search" and query:
                    # Perform search operation
                    yield f"data: {json.dumps({'type': 'status', 'message': f'Searching for: {query}'})}\n\n"

                    # Call the search function
                    search_func = webcat_functions.get("search")
                    if search_func:
                        result = await search_func(query)

                        # Limit results if specified
                        if (
                            result.get("results")
                            and len(result["results"]) > max_results
                        ):
                            result["results"] = result["results"][:max_results]
                            result["note"] = f"Results limited to {max_results} items"

                        yield f"data: {json.dumps({'type': 'data', 'data': result})}\n\n"
                        num_results = len(result.get("results", []))
                        yield f"data: {json.dumps({'type': 'complete', 'message': f'Search completed. Found {num_results} results.'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Search function not available'})}\n\n"

                elif operation == "health":
                    # Perform health check
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Checking server health...'})}\n\n"

                    health_func = webcat_functions.get("health_check")
                    if health_func:
                        result = await health_func()
                        yield f"data: {json.dumps({'type': 'data', 'data': result})}\n\n"
                        yield f"data: {json.dumps({'type': 'complete', 'message': 'Health check completed'})}\n\n"
                    else:
                        basic_health = {
                            "status": "healthy",
                            "service": "webcat-demo",
                            "timestamp": time.time(),
                        }
                        yield f"data: {json.dumps({'type': 'data', 'data': basic_health})}\n\n"
                        yield f"data: {json.dumps({'type': 'complete', 'message': 'Basic health check completed'})}\n\n"

                else:
                    # Just connection - send server info
                    server_info = {
                        "service": "WebCat MCP Demo Server",
                        "version": "2.2.0",
                        "status": "connected",
                        "operations": ["search", "health"],
                        "timestamp": time.time(),
                    }
                    yield f"data: {json.dumps({'type': 'data', 'data': server_info})}\n\n"
                    yield f"data: {json.dumps({'type': 'complete', 'message': 'Connection established'})}\n\n"

                # Keep alive with heartbeat
                heartbeat_count = 0
                while True:
                    await asyncio.sleep(30)
                    heartbeat_count += 1
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time(), 'count': heartbeat_count})}\n\n"

            except Exception as e:
                logger.error(f"Error in SSE stream: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return StreamingResponse(
            generate_webcat_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    # Mount FastMCP server as a sub-application (like Clima project)
    app.mount("/mcp", mcp_server.sse_app())

    logger.info("FastAPI app configured with SSE and FastMCP integration")
    return app


def run_simple_demo(host: str = "0.0.0.0", port: int = 8000):
    """Run the simplified WebCat demo server."""

    # Initialize the app
    app = create_demo_app()

    # Log endpoints
    logger.info(f"WebCat Demo Server: http://{host}:{port}")
    logger.info(f"SSE Demo Endpoint: http://{host}:{port}/sse")
    logger.info(f"FastMCP Endpoint: http://{host}:{port}/mcp")
    logger.info(f"Health Check: http://{host}:{port}/health")
    logger.info(f"Demo Client: http://{host}:{port}/client")
    logger.info(f"Server Status: http://{host}:{port}/status")

    print("\n🐱 WebCat MCP Demo Server Starting...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"🔗 SSE Demo: http://{host}:{port}/sse")
    print(f"🛠️ FastMCP: http://{host}:{port}/mcp")
    print(f"💗 Health: http://{host}:{port}/health")
    print(f"🎨 Demo UI: http://{host}:{port}/client")
    print(f"📊 Server Status: http://{host}:{port}/status")
    print("\n✨ Ready for connections!")

    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_simple_demo(port=port)
