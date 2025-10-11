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

logger = logging.getLogger(__name__)

# Get API keys from environment
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")


async def search_tool(query: str, max_results: int = 5) -> dict:
    """Search the web for information on a given query.

    This MCP tool searches the web using Serper API, Tavily API, or DuckDuckGo
    with automatic fallback. It automatically scrapes and converts content to markdown.

    Fallback order:
    1. Serper API (if SERPER_API_KEY configured)
    2. Tavily API (if TAVILY_API_KEY configured)
    3. DuckDuckGo (free, always available)

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Dict representation of SearchResponse model (for MCP JSON serialization)
    """
    logger.info(f"Processing search request: {query} (max {max_results} results)")

    # Fetch results with automatic fallback
    api_results, search_source = fetch_with_fallback(
        query, SERPER_API_KEY, TAVILY_API_KEY, max_results
    )

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
