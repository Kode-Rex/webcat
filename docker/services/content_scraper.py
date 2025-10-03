# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Content scraper service - extracts and converts web content to markdown."""

import logging

import html2text
import requests
from bs4 import BeautifulSoup
from readability import Document

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


def _configure_html2text() -> html2text.HTML2Text:
    """Configure html2text converter with optimal settings.

    Returns:
        Configured HTML2Text instance
    """
    h = html2text.HTML2Text()
    h.ignore_links = True  # Skip navigation links
    h.ignore_images = True  # Skip images for cleaner output
    h.body_width = 0  # No wrapping
    h.unicode_snob = True  # Use Unicode instead of ASCII
    h.escape_snob = False  # Escape special chars for safety
    h.use_automatic_links = False  # Avoid extra link noise
    h.mark_code = False  # Let code blocks be handled naturally
    h.single_line_break = True  # More compact output
    h.ignore_emphasis = False  # Keep bold/italic
    h.skip_internal_links = True  # Skip internal navigation
    return h


def _extract_language_from_classes(classes: list) -> str:
    """Extract programming language from CSS classes.

    Args:
        classes: List of CSS class names

    Returns:
        Language identifier or empty string if not found
    """
    known_languages = [
        "python",
        "javascript",
        "css",
        "html",
        "java",
        "php",
        "c",
        "cpp",
        "csharp",
        "ruby",
        "go",
    ]
    for cls in classes:
        if cls.startswith(("language-", "lang-")):
            return cls.replace("language-", "").replace("lang-", "")
        if cls in known_languages:
            return cls
    return ""


def _process_code_blocks(soup: BeautifulSoup) -> None:
    """Add language tags to code blocks when possible.

    Args:
        soup: BeautifulSoup object to modify in-place
    """
    for pre in soup.find_all("pre"):
        if pre.code and pre.code.get("class"):
            language = _extract_language_from_classes(pre.code.get("class"))
            if language:
                pre.insert_before(f"```{language}")
                pre.insert_after("```")


def _process_math_elements(soup: BeautifulSoup) -> None:
    """Preserve LaTeX/MathJax markup in HTML.

    Args:
        soup: BeautifulSoup object to modify in-place
    """
    math_script_types = [
        "math/tex",
        "math/tex; mode=display",
        "application/x-mathjax-config",
    ]
    for math in soup.find_all(["math", "script"]):
        if math.name == "script" and math.get("type") in math_script_types:
            math.replace_with(f"$$${math.string}$$$")
        elif math.name == "math":
            math.replace_with(f"$$${str(math)}$$$")


def _clean_soup(soup: BeautifulSoup) -> None:
    """Remove unwanted elements from soup.

    Args:
        soup: BeautifulSoup object to clean in-place
    """
    # Remove common navigation and UI elements
    unwanted_selectors = [
        "nav",
        "header",
        "footer",
        "aside",
        ".nav",
        ".navigation",
        ".navbar",
        ".menu",
        ".header",
        ".footer",
        ".sidebar",
        ".ad",
        ".advertisement",
        ".social",
        ".share",
        ".comments",
        ".cookie",
        ".popup",
        '[role="navigation"]',
        '[role="banner"]',
        '[role="complementary"]',
        '[aria-label="navigation"]',
    ]

    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Remove script and style tags
    for tag in soup(["script", "style", "iframe", "noscript"]):
        tag.decompose()


def _convert_to_markdown(html_content: str, title: str, url: str) -> str:
    """Convert HTML to markdown with preprocessing.

    Args:
        html_content: HTML content to convert
        title: Document title
        url: Source URL

    Returns:
        Markdown-formatted content with title and metadata
    """
    h = _configure_html2text()
    soup = BeautifulSoup(html_content, "html.parser")
    _clean_soup(soup)
    _process_code_blocks(soup)
    _process_math_elements(soup)
    markdown_text = h.handle(str(soup))

    # Clean up excessive whitespace
    lines = [line.strip() for line in markdown_text.split("\n") if line.strip()]
    markdown_text = "\n\n".join(lines)

    return f"# {title}\n\n*Source: {url}*\n\n{markdown_text}"


def _convert_with_readability(response_content: bytes, url: str) -> str:
    """Extract and convert main content using Readability.

    Args:
        response_content: Raw HTML bytes from response
        url: Source URL for metadata

    Returns:
        Markdown-formatted content

    Raises:
        Exception: If Readability extraction fails
    """
    doc = Document(response_content)
    title = doc.title()
    return _convert_to_markdown(doc.summary(), title, url)


def _convert_fallback(response_content: bytes, fallback_title: str, url: str) -> str:
    """Convert HTML to markdown without Readability extraction.

    Args:
        response_content: Raw HTML bytes from response
        fallback_title: Title to use if extraction fails
        url: Source URL for metadata

    Returns:
        Markdown-formatted content
    """
    h = _configure_html2text()
    soup = BeautifulSoup(response_content, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.text if title_tag else fallback_title
    return f"# {title}\n\n*Source: {url}*\n\n{h.handle(str(soup))}"


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

    Args:
        result: SearchResult object with URL to scrape

    Returns:
        Updated SearchResult with content in markdown format
    """
    if not result.url:
        result.content = "Error: Missing URL for content scraping."
        return result

    try:
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

        try:
            full_content = _convert_with_readability(response.content, result.url)
        except Exception as e:
            logger.warning(
                f"Readability parsing failed: {str(e)}. Falling back to direct HTML parsing."
            )
            full_content = _convert_fallback(response.content, result.title, result.url)

        result.content = _truncate_if_needed(full_content)
        return result
    except requests.RequestException as e:
        result.content = f"Error: Failed to retrieve the webpage. {str(e)}"
        return result
    except Exception as e:
        result.content = f"Error: Failed to scrape content. {str(e)}"
        return result
