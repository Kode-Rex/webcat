# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Perplexity API client - deep research search using Perplexity's sonar models."""

import logging
from typing import List, Literal

from perplexity import Perplexity

logger = logging.getLogger(__name__)


def fetch_perplexity_deep_research(
    query: str,
    api_key: str,
    max_results: int = 5,
    research_effort: Literal["low", "medium", "high"] = "high",
) -> tuple[str, List[str]]:
    """
    Fetch deep research results from Perplexity AI using official SDK.

    Uses Perplexity's sonar-deep-research model which performs dozens of searches,
    reads hundreds of sources, and reasons through material to deliver comprehensive
    research reports. This is ideal for in-depth analysis and multi-source synthesis.

    Args:
        query: The research query/question
        api_key: Perplexity API key
        max_results: Maximum number of results to return (default: 5)
        research_effort: Computational effort level - "low" (fast), "medium" (balanced),
                        or "high" (deepest research). Only applies to sonar-deep-research.

    Returns:
        Tuple of (research_report: str, citations: List[str])
        - research_report: Full synthesized research content in markdown
        - citations: List of citation URLs used in the research
    """
    try:
        logger.info(
            f"Fetching Perplexity deep research (effort: {research_effort}): {query}"
        )

        # Initialize Perplexity client with 10-minute timeout for deep research
        client = Perplexity(api_key=api_key, timeout=600.0)

        # Create chat completion with deep research
        # Note: Official SDK may not support all parameters, using minimal set
        response = client.chat.completions.create(
            model="sonar-deep-research",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a comprehensive research assistant. Provide detailed, "
                        "well-researched answers with clear structure and citations. "
                        f"Focus on returning {max_results} most relevant sources."
                    ),
                },
                {"role": "user", "content": query},
            ],
        )

        # Extract research content
        research_report = ""
        citation_urls: List[str] = []

        if response.choices and len(response.choices) > 0:
            research_report = response.choices[0].message.content or ""

            # Extract citations from response
            if hasattr(response, "citations") and response.citations:
                citation_urls = [
                    citation if isinstance(citation, str) else citation.get("url", "")
                    for citation in response.citations
                    if citation
                ][:max_results]

            token_count = (
                response.usage.total_tokens if hasattr(response, "usage") else "N/A"
            )
            logger.info(
                f"Perplexity deep research completed: {len(research_report)} chars, "
                f"{len(citation_urls)} citations, {token_count} tokens"
            )

        return research_report, citation_urls

    except Exception as e:
        logger.exception(f"Error fetching Perplexity deep research: {str(e)}")
        return "", []
