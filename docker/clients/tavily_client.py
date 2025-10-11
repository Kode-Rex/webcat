# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Tavily API client - search and content extraction via Tavily API."""

import logging
from typing import List, Optional

from tavily import TavilyClient

from models.api_search_result import APISearchResult

logger = logging.getLogger(__name__)


def fetch_search_results(
    query: str, api_key: str, max_results: int = 5
) -> List[APISearchResult]:
    """
    Fetches search results from the Tavily API.

    Args:
        query: The search query
        api_key: The Tavily API key
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A list of APISearchResult objects from Tavily API
    """
    try:
        logger.info(f"Fetching Tavily search results for: {query}")

        # Initialize Tavily client
        client = TavilyClient(api_key=api_key)

        # Search with content extraction
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",  # Get most relevant sources
            include_raw_content=False,  # We'll extract separately for consistency
        )

        # Convert to APISearchResult objects
        results = []
        if "results" in response:
            for result in response["results"][:max_results]:
                results.append(
                    APISearchResult(
                        title=result.get("title", "Untitled"),
                        link=result.get("url", ""),
                        snippet=result.get("content", ""),
                    )
                )

        logger.info(f"Tavily returned {len(results)} search results")
        return results

    except Exception as e:
        logger.error(f"Error fetching Tavily search results: {str(e)}")
        return []


def extract_content(url: str, api_key: str) -> Optional[str]:
    """
    Extracts content from a URL using Tavily's Extract API.

    Uses Tavily's proprietary AI to extract only the most relevant content,
    optimized for context quality and size.

    Args:
        url: The URL to extract content from
        api_key: The Tavily API key

    Returns:
        Extracted content as markdown string, or None if extraction fails
    """
    try:
        logger.info(f"Extracting content via Tavily: {url}")

        # Initialize Tavily client
        client = TavilyClient(api_key=api_key)

        # Extract content
        response = client.extract(urls=[url])

        # Get the raw content from the response
        if (
            "results" in response
            and len(response["results"]) > 0
            and "raw_content" in response["results"][0]
        ):
            content = response["results"][0]["raw_content"]

            if content:
                logger.info(f"Tavily extracted {len(content)} chars from {url}")
                return content

        logger.warning(f"No content extracted by Tavily for {url}")
        return None

    except Exception as e:
        logger.error(f"Error extracting content via Tavily: {str(e)}")
        return None
