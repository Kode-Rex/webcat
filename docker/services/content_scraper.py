# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Content scraper service - extracts and converts web content to markdown."""

import logging
import os

import requests
import trafilatura

from clients.serper_client import scrape_webpage as serper_scrape_webpage
from constants import MAX_CONTENT_LENGTH, REQUEST_TIMEOUT_SECONDS
from models.search_result import SearchResult

logger = logging.getLogger(__name__)


def _fetch_content(url: str) -> requests.Response:
    """Fetch content from URL with browser-like headers.

    Args:
        url: URL to fetch

    Returns:
        HTTP response object

    Raises:
        requests.RequestException: If request fails
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS, headers=headers)
    response.raise_for_status()
    return response


def _handle_plain_text(response: requests.Response, result: SearchResult) -> str:
    """Convert plain text response to markdown format.

    Args:
        response: HTTP response containing plain text
        result: SearchResult with title and URL

    Returns:
        Markdown-formatted content
    """
    return f"# {result.title}\n\n*Source: {result.url}*\n\n```\n{response.text[:8000]}\n```"


def _handle_binary_content(content_type: str, result: SearchResult) -> str:
    """Create message for binary content that cannot be converted.

    Args:
        content_type: MIME type of binary content
        result: SearchResult with title and URL

    Returns:
        Markdown message explaining binary content
    """
    return f"# {result.title}\n\n*Source: {result.url}*\n\n**Note:** This content appears to be a binary file ({content_type}) and cannot be converted to markdown. Please download the file directly from the source URL."


def _truncate_if_needed(content: str) -> str:
    """Truncate content if it exceeds maximum length.

    Args:
        content: Content to check and truncate

    Returns:
        Original or truncated content
    """
    if len(content) > MAX_CONTENT_LENGTH:
        return content[:MAX_CONTENT_LENGTH] + "... [content truncated]"
    return content


def scrape_search_result(result: SearchResult) -> SearchResult:
    """
    Scrapes the content of a search result URL and converts it to markdown.

    Uses Serper's scrape API if SERPER_API_KEY is available (faster, more reliable).
    Falls back to Trafilatura for local scraping if Serper is not configured.

    Args:
        result: SearchResult object with URL to scrape

    Returns:
        Updated SearchResult with content in markdown format
    """
    if not result.url:
        result.content = "Error: Missing URL for content scraping."
        return result

    # Try Serper scraping first if API key is available
    serper_api_key = os.environ.get("SERPER_API_KEY", "")
    if serper_api_key:
        try:
            logger.info(f"Using Serper scrape API for {result.url}")
            scraped_content = serper_scrape_webpage(result.url, serper_api_key)

            if scraped_content:
                # Format with title and source
                full_content = (
                    f"# {result.title}\n\n*Source: {result.url}*\n\n{scraped_content}"
                )
                result.content = _truncate_if_needed(full_content)
                logger.info(
                    f"Successfully scraped via Serper: {len(result.content)} chars"
                )
                return result

            logger.warning(
                f"Serper scrape returned no content for {result.url}, falling back to Trafilatura"
            )
        except Exception as e:
            logger.warning(
                f"Serper scrape failed for {result.url}: {str(e)}, falling back to Trafilatura"
            )

    # Fallback to Trafilatura scraping
    try:
        logger.info(f"Using Trafilatura for {result.url}")
        response = _fetch_content(result.url)
        content_type = response.headers.get("Content-Type", "").lower()

        if "text/plain" in content_type:
            result.content = _handle_plain_text(response, result)
            return result

        if (
            "application/pdf" in content_type
            or "application/octet-stream" in content_type
        ):
            result.content = _handle_binary_content(content_type, result)
            return result

        # Use Trafilatura for clean article extraction
        extracted = trafilatura.extract(
            response.content,
            output_format="markdown",
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            url=result.url,
        )

        if extracted and len(extracted.strip()) > 100:
            # Remove first line if it's a duplicate title (common in Trafilatura output)
            lines = extracted.split("\n", 1)
            if (
                len(lines) > 1
                and lines[0].strip().lstrip("#").strip().lower() in result.title.lower()
            ):
                extracted = lines[1].lstrip()

            full_content = f"# {result.title}\n\n*Source: {result.url}*\n\n{extracted}"
            result.content = _truncate_if_needed(full_content)
            return result

        # Fallback if Trafilatura fails
        logger.warning(f"Trafilatura extraction failed for {result.url}")
        result.content = f"# {result.title}\n\n*Source: {result.url}*\n\n{result.snippet}\n\n(Full content extraction failed - only snippet available)"
        return result
    except requests.RequestException as e:
        result.content = f"Error: Failed to retrieve the webpage. {str(e)}"
        return result
    except Exception as e:
        result.content = f"Error: Failed to scrape content. {str(e)}"
        return result
