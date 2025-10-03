# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""FastAPI app factory functions."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from constants import VERSION
from endpoints.health_endpoints import setup_health_endpoints


def create_health_app() -> FastAPI:
    """Create a separate FastAPI app for health endpoints."""
    app = FastAPI(
        title="WebCat MCP Health Service",
        description="Health monitoring and demo client for WebCat MCP server",
        version=VERSION,
    )

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
        version=VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    setup_health_endpoints(app)
    return app
