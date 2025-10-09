# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Authentication utilities for WebCat server.

This module provides optional bearer token authentication. If WEBCAT_API_KEY
is set in the environment, MCP tool calls must include a valid bearer token
in the context. If not set, no authentication is required.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def validate_bearer_token(ctx: Optional[Any] = None) -> tuple[bool, Optional[str]]:
    """Validate bearer token if WEBCAT_API_KEY is set.

    Args:
        ctx: Optional context from MCP tool call (may contain request headers)

    Returns:
        Tuple of (is_valid, error_message)
        - If WEBCAT_API_KEY not set: (True, None) - no auth required
        - If valid token: (True, None)
        - If invalid/missing token: (False, error_message)
    """
    api_key = os.environ.get("WEBCAT_API_KEY")

    # No API key configured - no authentication required
    if not api_key:
        return True, None

    # API key is set - authentication required
    if ctx is None:
        logger.warning("Authentication required but no context provided")
        return False, "Authentication required: missing bearer token"

    # Try to extract Authorization header from context
    # FastMCP may provide headers in various ways depending on transport
    headers = None
    if hasattr(ctx, "headers"):
        headers = ctx.headers
    elif isinstance(ctx, dict) and "headers" in ctx:
        headers = ctx["headers"]

    if headers is None:
        logger.warning("Authentication required but no headers in context")
        return False, "Authentication required: missing bearer token"

    # Get Authorization header (case-insensitive)
    auth_header = None
    if isinstance(headers, dict):
        # Try different case variations
        auth_header = (
            headers.get("Authorization")
            or headers.get("authorization")
            or headers.get("AUTHORIZATION")
        )

    if not auth_header:
        logger.warning("Missing Authorization header")
        return False, "Authentication required: missing Authorization header"

    # Validate bearer token format
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Invalid Authorization header format")
        return (
            False,
            "Invalid Authorization header format. Expected: Bearer <token>",
        )

    token = parts[1]

    # Validate token
    if token != api_key:
        logger.warning("Invalid bearer token provided")
        return False, "Invalid bearer token"

    # Token is valid
    logger.debug("Bearer token validated successfully")
    return True, None
