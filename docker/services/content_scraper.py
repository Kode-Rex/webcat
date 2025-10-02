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
        # Add request headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

        response = requests.get(
            result.url, timeout=REQUEST_TIMEOUT_SECONDS, headers=headers
        )
        response.raise_for_status()

        # Check content type to handle different file types
        content_type = response.headers.get("Content-Type", "").lower()

        # Handle plain text
        if "text/plain" in content_type:
            result.content = f"# {result.title}\n\n*Source: {result.url}*\n\n```\n{response.text[:8000]}\n```"
            return result

        # Handle PDF and other binary formats
        if (
            "application/pdf" in content_type
            or "application/octet-stream" in content_type
        ):
            result.content = f"# {result.title}\n\n*Source: {result.url}*\n\n**Note:** This content appears to be a binary file ({content_type}) and cannot be converted to markdown. Please download the file directly from the source URL."
            return result

        # Use readability to extract the main content
        try:
            doc = Document(response.content)
            title = doc.title()

            # Convert HTML to Markdown using html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0  # No wrapping
            h.unicode_snob = True  # Use Unicode instead of ASCII
            h.escape_snob = True  # Don't escape special chars
            h.use_automatic_links = True  # Auto-link URLs
            h.mark_code = True  # Use markdown syntax for code blocks
            h.single_line_break = False  # Use two line breaks for paragraphs
            h.table_border_style = "html"  # Use HTML table borders
            h.images_to_alt = False  # Include image URLs
            h.protect_links = True  # Don't convert links to references

            # Pre-process HTML to handle special elements
            soup = BeautifulSoup(doc.summary(), "html.parser")

            # Handle code blocks better - ensure they have language tags when possible
            for pre in soup.find_all("pre"):
                if pre.code and pre.code.get("class"):
                    classes = pre.code.get("class")
                    # Look for language classes like 'language-python', 'python', etc.
                    language = None
                    for cls in classes:
                        if cls.startswith(("language-", "lang-")) or cls in [
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
                        ]:
                            language = cls.replace("language-", "").replace("lang-", "")
                            break

                    if language:
                        # Wrap in markdown code fence with language
                        pre.insert_before(f"```{language}")
                        pre.insert_after("```")

            # Handle LaTeX/MathJax by preserving the markup
            for math in soup.find_all(["math", "script"]):
                if math.name == "script" and math.get("type") in [
                    "math/tex",
                    "math/tex; mode=display",
                    "application/x-mathjax-config",
                ]:
                    # Preserve math content
                    math.replace_with(f"$$${math.string}$$$")
                elif math.name == "math":
                    # Preserve MathML
                    math.replace_with(f"$$${str(math)}$$$")

            # Get the markdown content
            markdown_text = h.handle(str(soup))

            # Add title and metadata at the beginning
            full_content = f"# {title}\n\n*Source: {result.url}*\n\n{markdown_text}"

        except Exception as e:
            # Fallback to direct HTML to Markdown conversion if readability fails
            logger.warning(
                f"Readability parsing failed: {str(e)}. Falling back to direct HTML parsing."
            )
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0

            soup = BeautifulSoup(response.content, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.text if title_tag else result.title

            full_content = (
                f"# {title}\n\n*Source: {result.url}*\n\n{h.handle(str(soup))}"
            )

        # Limit content length to prevent huge responses
        if len(full_content) > MAX_CONTENT_LENGTH:
            full_content = (
                full_content[:MAX_CONTENT_LENGTH] + "... [content truncated]"
            )

        result.content = full_content
        return result
    except requests.RequestException as e:
        result.content = f"Error: Failed to retrieve the webpage. {str(e)}"
        return result
    except Exception as e:
        result.content = f"Error: Failed to scrape content. {str(e)}"
        return result
