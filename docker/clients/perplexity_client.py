# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Perplexity API client - deep research search using Perplexity's sonar models."""

import json
import logging
from typing import List, Literal

import requests

logger = logging.getLogger(__name__)


def fetch_perplexity_deep_research(
    query: str,
    api_key: str,
    max_results: int = 5,
    research_effort: Literal["low", "medium", "high"] = "high",
) -> tuple[str, List[str]]:
    """
    Fetch deep research results from Perplexity AI.

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
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sonar-deep-research",
        "messages": [
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
        "reasoning_effort": research_effort,
        "return_citations": True,
        "return_related_questions": False,
        "search_domain_filter": [],  # Search all domains
        "temperature": 0.2,  # Lower temperature for factual research
    }

    try:
        logger.info(
            f"Fetching Perplexity deep research (effort: {research_effort}): {query}"
        )
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        # Extract the main research content
        research_report = ""
        citation_urls: List[str] = []

        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            message = choice.get("message", {})
            research_report = message.get("content", "")

            # Extract citation URLs
            citations = data.get("citations", [])
            citation_urls = [
                citation.get("url", "") for citation in citations if citation.get("url")
            ][:max_results]

            token_count = data.get("usage", {}).get("total_tokens", "N/A")
            logger.info(
                f"Perplexity deep research completed: {len(research_report)} chars, "
                f"{len(citation_urls)} citations, {token_count} tokens"
            )

        return research_report, citation_urls

    except requests.exceptions.HTTPError as e:
        logger.error(f"Perplexity API HTTP error: {e.response.status_code} - {e}")
        if e.response.status_code == 401:
            logger.error("Invalid Perplexity API key")
        elif e.response.status_code == 429:
            logger.error("Perplexity API rate limit exceeded")
        return "", []
    except Exception as e:
        logger.error(f"Error fetching Perplexity deep research: {str(e)}")
        return "", []
