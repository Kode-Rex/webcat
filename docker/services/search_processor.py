# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search processor service - processes API results into enriched search results."""

from typing import List

from models.api_search_result import APISearchResult
from models.search_result import SearchResult
from services.content_scraper import scrape_search_result


def process_search_results(results: List[APISearchResult]) -> List[SearchResult]:
    """
    Processes API search results into SearchResult objects with scraped content.

    Args:
        results: List of APISearchResult objects from search APIs

    Returns:
        List of SearchResult objects with scraped content
    """
    processed_results: List[SearchResult] = []

    for api_result in results:
        # Create a SearchResult object from API result
        search_result = SearchResult(
            title=api_result.title,
            url=api_result.link,
            snippet=api_result.snippet,
        )

        # Scrape content for the result
        search_result = scrape_search_result(search_result)
        processed_results.append(search_result)

    return processed_results
