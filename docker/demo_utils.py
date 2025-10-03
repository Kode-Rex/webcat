# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Shared utilities for demo servers."""

import json
import time


def format_sse_message(message_type: str, **kwargs) -> str:
    """Format SSE message.

    Args:
        message_type: Message type
        **kwargs: Additional message fields

    Returns:
        Formatted SSE message string
    """
    data = {"type": message_type, **kwargs}
    return f"data: {json.dumps(data)}\n\n"


async def handle_search_operation(search_func, query: str, max_results: int):
    """Handle search operation and yield results.

    Args:
        search_func: Search function to call
        query: Search query
        max_results: Maximum results to return

    Yields:
        SSE formatted messages
    """
    yield format_sse_message("status", message=f"Searching for: {query}")

    result = await search_func(query)

    # Limit results if needed
    if result.get("results") and len(result["results"]) > max_results:
        result["results"] = result["results"][:max_results]
        result["note"] = f"Results limited to {max_results} items"

    yield format_sse_message("data", data=result)
    num_results = len(result.get("results", []))
    yield format_sse_message(
        "complete", message=f"Search completed. Found {num_results} results."
    )


async def handle_health_operation(health_func):
    """Handle health check operation.

    Args:
        health_func: Health check function to call (or None)

    Yields:
        SSE formatted messages
    """
    yield format_sse_message("status", message="Checking server health...")

    if health_func:
        result = await health_func()
        yield format_sse_message("data", data=result)
        yield format_sse_message("complete", message="Health check completed")
    else:
        basic_health = {
            "status": "healthy",
            "service": "webcat-demo",
            "timestamp": time.time(),
        }
        yield format_sse_message("data", data=basic_health)
        yield format_sse_message("complete", message="Basic health check completed")


def get_server_info() -> dict:
    """Get server information dictionary.

    Returns:
        Server info dictionary
    """
    return {
        "service": "WebCat MCP Demo Server",
        "version": "2.2.0",
        "status": "connected",
        "operations": ["search", "health"],
        "timestamp": time.time(),
    }
