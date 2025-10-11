# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search service - unified search logic with automatic fallback."""

import logging
from typing import List, Tuple

from clients.duckduckgo_client import fetch_duckduckgo_search_results
from clients.serper_client import fetch_search_results as serper_fetch_search_results
from clients.tavily_client import fetch_search_results as tavily_fetch_search_results
from models.api_search_result import APISearchResult

logger = logging.getLogger(__name__)


def fetch_with_fallback(
    query: str,
    serper_api_key: str = "",
    tavily_api_key: str = "",
    max_results: int = 5,
) -> Tuple[List[APISearchResult], str]:
    """
    Fetch search results with automatic fallback chain.

    Fallback order:
    1. Serper API (if key provided)
    2. Tavily API (if key provided)
    3. DuckDuckGo (free, always available)

    Args:
        query: Search query string
        serper_api_key: Optional Serper API key
        tavily_api_key: Optional Tavily API key
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Tuple of (results list, source name)
    """
    api_results: List[APISearchResult] = []
    search_source: str = "Unknown"

    # Try Serper API first if key is available
    if serper_api_key:
        logger.info("Using Serper API for search")
        search_source = "Serper API"
        api_results = serper_fetch_search_results(query, serper_api_key, max_results)

    # Fall back to Tavily if Serper unavailable or failed
    if not api_results and tavily_api_key:
        logger.info("Using Tavily API for search (Serper unavailable)")
        search_source = "Tavily API"
        api_results = tavily_fetch_search_results(query, tavily_api_key, max_results)

    # Fall back to DuckDuckGo if no API keys or no results
    if not api_results:
        _log_fallback_reason(serper_api_key, tavily_api_key)
        search_source = "DuckDuckGo (free fallback)"
        api_results = fetch_duckduckgo_search_results(query, max_results)

    return api_results, search_source


def _log_fallback_reason(serper_api_key: str, tavily_api_key: str) -> None:
    """Log why we're falling back to DuckDuckGo."""
    if not serper_api_key and not tavily_api_key:
        logger.info("No premium API keys configured, using DuckDuckGo fallback")
    elif not serper_api_key:
        logger.warning("No results from Tavily API, trying DuckDuckGo fallback")
    elif not tavily_api_key:
        logger.warning("No results from Serper API, trying DuckDuckGo fallback")
    else:
        logger.warning(
            "No results from Serper or Tavily APIs, trying DuckDuckGo fallback"
        )
