# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search orchestration service for managing search requests and fallbacks."""

import asyncio
import logging
from typing import Any, Dict, List, Tuple

from clients.duckduckgo_client import fetch_duckduckgo_search_results
from clients.serper_client import fetch_search_results
from models.api_search_result import APISearchResult
from services.search_processor import process_search_results

logger = logging.getLogger(__name__)


async def fetch_with_serper(
    query: str, api_key: str
) -> Tuple[List[APISearchResult], str]:
    """Fetch search results using Serper API.

    Args:
        query: Search query
        api_key: Serper API key

    Returns:
        Tuple of (results, search_source)
    """
    logger.info("Using Serper API for search")
    results = await asyncio.get_event_loop().run_in_executor(
        None, fetch_search_results, query, api_key
    )
    return results, "Serper API"


async def fetch_with_duckduckgo(
    query: str, has_api_key: bool
) -> Tuple[List[APISearchResult], str]:
    """Fetch search results using DuckDuckGo.

    Args:
        query: Search query
        has_api_key: Whether Serper API key was configured

    Returns:
        Tuple of (results, search_source)
    """
    if not has_api_key:
        logger.info("No Serper API key configured, using DuckDuckGo fallback")
    else:
        logger.warning("No results from Serper API, trying DuckDuckGo fallback")

    results = await asyncio.get_event_loop().run_in_executor(
        None, fetch_duckduckgo_search_results, query
    )
    return results, "DuckDuckGo (free fallback)"


def format_no_results_error(query: str, search_source: str) -> Dict[str, Any]:
    """Format error response for no results.

    Args:
        query: Search query
        search_source: Source that was used

    Returns:
        Error dictionary
    """
    return {
        "error": "No search results found from any source.",
        "query": query,
        "search_source": search_source,
    }


def format_search_error(error: str, query: str, search_source: str) -> Dict[str, Any]:
    """Format error response for search failure.

    Args:
        error: Error message
        query: Search query
        search_source: Source that was attempted

    Returns:
        Error dictionary
    """
    return {
        "error": f"Search failed: {error}",
        "query": query,
        "search_source": search_source,
    }


async def process_and_format_results(
    results: List[APISearchResult], query: str, search_source: str
) -> Dict[str, Any]:
    """Process search results and format response.

    Args:
        results: Raw search results
        query: Search query
        search_source: Source of results

    Returns:
        Formatted results dictionary
    """
    processed_results = await asyncio.get_event_loop().run_in_executor(
        None, process_search_results, results
    )

    return {
        "query": query,
        "search_source": search_source,
        "results": [result.model_dump() for result in processed_results],
    }


async def execute_search(query: str, serper_api_key: str = "") -> Dict[str, Any]:
    """Execute search with automatic fallback logic.

    Args:
        query: Search query
        serper_api_key: Optional Serper API key

    Returns:
        Formatted search results dictionary
    """
    results: List[APISearchResult] = []
    search_source = "Unknown"

    try:
        # Try Serper API first if key is available
        if serper_api_key:
            results, search_source = await fetch_with_serper(query, serper_api_key)

        # Fall back to DuckDuckGo if no API key or no results from Serper
        if not results:
            results, search_source = await fetch_with_duckduckgo(
                query, bool(serper_api_key)
            )

        # Check if we got any results
        if not results:
            logger.warning(f"No search results found for query: {query}")
            return format_no_results_error(query, search_source)

        # Process and format results
        return await process_and_format_results(results, query, search_source)

    except Exception as e:
        logger.error(f"Error in search function: {str(e)}")
        return format_search_error(str(e), query, search_source)
