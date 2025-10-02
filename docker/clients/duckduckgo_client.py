# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""DuckDuckGo client - fetches search results from DuckDuckGo (free fallback)."""

import logging
from typing import List

from docker.models.api_search_result import APISearchResult

logger = logging.getLogger(__name__)

# Try to import DuckDuckGo search, it's an optional dependency
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None
    logger.warning(
        "duckduckgo-search not available. DuckDuckGo fallback will not work."
    )


def fetch_duckduckgo_search_results(
    query: str, max_results: int = 3
) -> List[APISearchResult]:
    """
    Fetches search results from DuckDuckGo as a free fallback.

    Args:
        query: The search query
        max_results: Maximum number of results to return

    Returns:
        A list of APISearchResult objects from DuckDuckGo
    """
    if not DDGS:
        logger.error("DuckDuckGo search not available (library not installed)")
        return []

    try:
        logger.info(f"Using DuckDuckGo fallback search for: {query}")

        with DDGS() as ddgs:
            # Get search results from DuckDuckGo
            results = []
            search_results = ddgs.text(query, max_results=max_results)

            for result in search_results:
                # Convert DuckDuckGo result format to APISearchResult
                results.append(
                    APISearchResult(
                        title=result.get("title", "Untitled"),
                        link=result.get("href", ""),
                        snippet=result.get("body", ""),
                    )
                )

            logger.info(f"DuckDuckGo returned {len(results)} results")
            return results

    except Exception as e:
        logger.error(f"Error fetching DuckDuckGo search results: {str(e)}")
        return []
