# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Deep research tool - comprehensive research using Perplexity's sonar-deep-research."""

import logging
import os
from typing import Literal

from clients.perplexity_client import fetch_perplexity_deep_research
from models.search_response import SearchResponse
from services.search_processor import process_search_results

logger = logging.getLogger(__name__)

# Get API key from environment
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")


async def deep_research_tool(
    query: str,
    research_effort: Literal["low", "medium", "high"] = "high",
    max_results: int = 5,
) -> dict:
    """Perform comprehensive deep research on a topic using Perplexity AI.

    This tool uses Perplexity's sonar-deep-research model which performs dozens of
    searches, reads hundreds of sources, and reasons through material to deliver
    comprehensive research reports. Ideal for in-depth analysis, multi-source synthesis,
    and thorough investigation of complex topics.

    Takes 2-4 minutes to complete what would take a human expert many hours.

    Args:
        query: The research question or topic to investigate
        research_effort: Computational depth - "low" (fast), "medium" (balanced),
                        or "high" (deepest, most comprehensive). Default: "high"
        max_results: Maximum number of source results to return (default: 5)

    Returns:
        Dict representation of SearchResponse with comprehensive research findings
    """
    logger.info(
        f"Deep research request: {query} (effort: {research_effort}, "
        f"max: {max_results})"
    )

    # Check if Perplexity API key is configured
    if not PERPLEXITY_API_KEY:
        logger.error("PERPLEXITY_API_KEY not configured")
        response = SearchResponse(
            query=query,
            search_source="Perplexity Deep Research (not configured)",
            results=[],
            error=(
                "Perplexity API key not configured. Please set PERPLEXITY_API_KEY "
                "environment variable to use deep research functionality."
            ),
        )
        return response.model_dump()

    # Fetch deep research results from Perplexity
    api_results = fetch_perplexity_deep_research(
        query=query,
        api_key=PERPLEXITY_API_KEY,
        max_results=max_results,
        research_effort=research_effort,
    )

    # Check if we got any results
    if not api_results:
        logger.warning(f"No deep research results found for query: {query}")
        response = SearchResponse(
            query=query,
            search_source="Perplexity Deep Research",
            results=[],
            error=(
                "Deep research failed. This could be due to API limits, "
                "invalid query, or temporary service issues."
            ),
        )
        return response.model_dump()

    # Process the results (scrape and convert to markdown)
    processed_results = process_search_results(api_results)

    # Build typed response
    response = SearchResponse(
        query=query,
        search_source=f"Perplexity Deep Research (effort: {research_effort})",
        results=processed_results,
    )

    logger.info(f"Deep research completed: {len(processed_results)} sources analyzed")
    return response.model_dump()
