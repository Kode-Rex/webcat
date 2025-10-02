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


def fetch_search_results(query: str, api_key: str) -> List[APISearchResult]:
    """
    Fetches search results from the Serper API.

    Args:
        query: The search query
        api_key: The Serper API key

    Returns:
        A list of APISearchResult objects from Serper API
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        # Process and return the search results
        if "organic" in data:
            # Convert to APISearchResult objects
            return [
                APISearchResult(
                    title=result.get("title", "Untitled"),
                    link=result.get("link", ""),
                    snippet=result.get("snippet", ""),
                )
                for result in data["organic"]
            ]
        return []
    except Exception as e:
        logger.error(f"Error fetching search results: {str(e)}")
        return []
