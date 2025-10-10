# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health and status endpoint handlers."""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from models.health_responses import (
    get_detailed_status,
    get_health_status,
    get_root_info,
    get_status_error,
    get_unhealthy_status,
)

logger = logging.getLogger(__name__)


def setup_health_endpoints(app: FastAPI):
    """Setup health and utility endpoints for the WebCat server."""

    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        try:
            return get_health_status()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(status_code=500, content=get_unhealthy_status(str(e)))

    @app.get("/status")
    async def server_status():
        """Detailed server status endpoint."""
        try:
            return get_detailed_status()
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return JSONResponse(status_code=500, content=get_status_error(str(e)))

    @app.get("/")
    async def root():
        """Root endpoint with basic information."""
        return get_root_info()
