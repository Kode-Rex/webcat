# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search tool - MCP tool for web search with automatic fallback."""

import logging
import os
from typing import List

from clients.duckduckgo_client import (
    fetch_duckduckgo_search_results as fetch_ddg_results,
)
from clients.serper_client import fetch_search_results
from models.api_search_result import APISearchResult
from models.search_response import SearchResponse
from models.search_result import SearchResult
from services.search_processor import process_search_results

logger = logging.getLogger(__name__)

# Get API key from environment
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")


async def search_tool(query: str, ctx=None) -> dict:
    """Search the web for information on a given query.

    This MCP tool searches the web using Serper API (premium) or DuckDuckGo
    (free fallback). It automatically scrapes and converts content to markdown.

    Args:
        query: The search query string
        ctx: Optional MCP context

    Returns:
        Dict representation of SearchResponse model (for MCP JSON serialization)
    """
    logger.info(f"Processing search request: {query}")

    # Typed as List[APISearchResult] - holds raw API responses
    api_results: List[APISearchResult] = []
    search_source: str = "Unknown"

    # Try Serper API first if key is available
    if SERPER_API_KEY:
        logger.info("Using Serper API for search")
        search_source = "Serper API"
        api_results = fetch_search_results(query, SERPER_API_KEY)

    # Fall back to DuckDuckGo if no API key or no results from Serper
    if not api_results:
        if not SERPER_API_KEY:
            logger.info("No Serper API key configured, using DuckDuckGo fallback")
        else:
            logger.warning("No results from Serper API, trying DuckDuckGo fallback")

        search_source = "DuckDuckGo (free fallback)"
        api_results = fetch_ddg_results(query)

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
