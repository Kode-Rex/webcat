# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search tool - MCP tool for web search with automatic fallback."""

import logging
import os
from typing import List

from models.search_response import SearchResponse
from models.search_result import SearchResult
from services.search_processor import process_search_results
from services.search_service import fetch_with_fallback
from utils.auth import validate_bearer_token

logger = logging.getLogger(__name__)

# Get API key from environment
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")


async def search_tool(query: str, ctx=None, max_results: int = 5) -> dict:
    """Search the web for information on a given query.

    This MCP tool searches the web using Serper API (premium) or DuckDuckGo
    (free fallback). It automatically scrapes and converts content to markdown.

    Args:
        query: The search query string
        ctx: Optional MCP context (may contain authentication headers)
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Dict representation of SearchResponse model (for MCP JSON serialization)
    """
    logger.info(f"Processing search request: {query} (max {max_results} results)")

    # Validate authentication if WEBCAT_API_KEY is set
    is_valid, error_msg = validate_bearer_token(ctx)
    if not is_valid:
        logger.warning(f"Authentication failed: {error_msg}")
        response = SearchResponse(
            query=query,
            search_source="none",
            results=[],
            error=error_msg,
        )
        return response.model_dump()

    # Fetch results with automatic fallback
    api_results, search_source = fetch_with_fallback(query, SERPER_API_KEY, max_results)

    # Check if we got any results
    if not api_results:
        logger.warning(f"No search results found for query: {query}")
        response = SearchResponse(
            query=query,
            search_source=search_source,
            results=[],
            error="No search results found from any source.",
        )
        # Only convert to dict at MCP boundary for JSON serialization
        return response.model_dump()

    # Process the results - typed as List[SearchResult]
    processed_results: List[SearchResult] = process_search_results(api_results)

    # Build typed response
    response = SearchResponse(
        query=query,
        search_source=search_source,
        results=processed_results,
    )
    # Only convert to dict at MCP boundary for JSON serialization
    return response.model_dump()
