# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search service - unified search logic with automatic fallback."""

import logging
from typing import List, Tuple

from clients.duckduckgo_client import fetch_duckduckgo_search_results
from clients.serper_client import fetch_search_results
from models.api_search_result import APISearchResult

logger = logging.getLogger(__name__)


def fetch_with_fallback(
    query: str, serper_api_key: str = ""
) -> Tuple[List[APISearchResult], str]:
    """
    Fetch search results with automatic fallback from Serper to DuckDuckGo.

    Args:
        query: Search query string
        serper_api_key: Optional Serper API key

    Returns:
        Tuple of (results list, source name)
    """
    api_results: List[APISearchResult] = []
    search_source: str = "Unknown"

    # Try Serper API first if key is available
    if serper_api_key:
        logger.info("Using Serper API for search")
        search_source = "Serper API"
        api_results = fetch_search_results(query, serper_api_key)

    # Fall back to DuckDuckGo if no API key or no results from Serper
    if not api_results:
        _log_fallback_reason(serper_api_key)
        search_source = "DuckDuckGo (free fallback)"
        api_results = fetch_duckduckgo_search_results(query)

    return api_results, search_source


def _log_fallback_reason(serper_api_key: str) -> None:
    """Log why we're falling back to DuckDuckGo."""
    if not serper_api_key:
        logger.info("No Serper API key configured, using DuckDuckGo fallback")
    else:
        logger.warning("No results from Serper API, trying DuckDuckGo fallback")
