#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Simplified demo server with FastMCP integration."""

import logging
import os
import tempfile

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from api_tools import create_webcat_functions, setup_webcat_tools
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
        title="WebCat MCP Server",
        description="WebCat server with FastMCP integration",
        version="2.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Setup health endpoints (this adds /health, /demo, /status, /)
    setup_health_endpoints(app)

    # Initialize FastMCP server
    mcp_server = FastMCP("WebCat Demo Server")

    # Setup WebCat tools
    webcat_functions = create_webcat_functions()
    setup_webcat_tools(mcp_server, webcat_functions)

    # Mount FastMCP server
    app.mount("/mcp", mcp_server.sse_app())

    logger.info("FastAPI app configured with FastMCP integration")
    return app


def run_simple_demo(host: str = "0.0.0.0", port: int = 8000):
    """Run the simplified WebCat demo server."""

    # Initialize the app
    app = create_demo_app()

    # Log endpoints
    logger.info(f"WebCat MCP Server: http://{host}:{port}")
    logger.info(f"FastMCP Endpoint: http://{host}:{port}/mcp")
    logger.info(f"Health Check: http://{host}:{port}/health")
    logger.info(f"Demo Client: http://{host}:{port}/demo")
    logger.info(f"Server Status: http://{host}:{port}/status")

    print("\n🐱 WebCat MCP Server Starting...")
    print(f"📡 Server: http://{host}:{port}")
    print(f"🛠️  MCP Endpoint: http://{host}:{port}/mcp")
    print(f"💗 Health: http://{host}:{port}/health")
    print(f"🎨 Demo UI: http://{host}:{port}/demo")
    print(f"📊 Status: http://{host}:{port}/status")
    print("\n✨ Ready for connections!")

    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_simple_demo(port=port)
