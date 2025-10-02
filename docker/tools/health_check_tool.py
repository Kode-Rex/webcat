# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health check tool - MCP tool for server health monitoring."""

from models.health_check_response import HealthCheckResponse


async def health_check_tool() -> dict:
    """Check the health of the server.

    This MCP tool provides a simple health check endpoint to verify
    the server is running and responsive.

    Returns:
        Dict representation of HealthCheckResponse model (for MCP JSON serialization)
    """
    # Build typed response
    response = HealthCheckResponse(status="healthy", service="webcat")
    # Only convert to dict at MCP boundary for JSON serialization
    return response.model_dump()
