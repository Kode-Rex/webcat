# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Serper API client - fetches search results from Serper API."""

import json
import logging
from typing import List

import requests

from models.api_search_result import APISearchResult

logger = logging.getLogger(__name__)


def _convert_organic_results(organic_results: list) -> List[APISearchResult]:
    """Convert organic search results to APISearchResult objects.

    Args:
        organic_results: List of organic result dictionaries from Serper API

    Returns:
        List of APISearchResult objects
    """
    return [
        APISearchResult(
            title=result.get("title", "Untitled"),
            link=result.get("link", ""),
            snippet=result.get("snippet", ""),
        )
        for result in organic_results
    ]


def fetch_search_results(
    query: str, api_key: str, max_results: int = 5
) -> List[APISearchResult]:
    """
    Fetches search results from the Serper API.

    Args:
        query: The search query
        api_key: The Serper API key
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A list of APISearchResult objects from Serper API
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": max_results})
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        # Process and return the search results
        if "organic" in data:
            results = _convert_organic_results(data["organic"])
            return results[:max_results]  # Ensure we don't exceed max_results
        return []
    except Exception as e:
        logger.error(f"Error fetching search results: {str(e)}")
        return []
