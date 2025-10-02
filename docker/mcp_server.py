# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Entry point for the WebCat server using FastMCP."""

import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

import html2text
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel
from readability import Document

# Set up logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.environ.get("LOG_DIR", tempfile.gettempdir())
LOG_FILE = os.path.join(LOG_DIR, "webcat.log")

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create formatters
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Setup console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Setup rotating file handler (10MB per file, keep 5 backup files)
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logging.info("Logging initialized with file rotation at %s", LOG_FILE)

# Load environment variables
load_dotenv()


# Import necessary modules for search functionality

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None
    logging.warning(
        "duckduckgo-search not available. DuckDuckGo fallback will not work."
    )


# Model definitions
class SearchResult(BaseModel):
    """Model for a single search result with scraped content."""

    title: str
    url: Optional[str] = ""
    snippet: str
    content: str = ""


class APISearchResult(BaseModel):
    """Raw search result from external API (Serper/DuckDuckGo)."""

    title: str
    link: str
    snippet: str

    class Config:
        """Pydantic config."""

        # Allow both 'link', 'url', and 'href' for compatibility
        extra = "allow"


class SearchResponse(BaseModel):
    """Response from the search tool."""

    query: str
    search_source: str
    results: List[SearchResult]
    error: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Response from health check tool."""

    status: str
    service: str


class ErrorResponse(BaseModel):
    """Error response format."""

    error: str
    query: Optional[str] = None
    details: Optional[str] = None


# Configure API keys
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

logging.info(
    f"Using SERPER API key from environment: {'Set' if SERPER_API_KEY else 'Not set'}"
)

# Create FastMCP instance (no authentication required)
mcp_server = FastMCP("WebCat Search")


# Utility functions
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
        logging.error(f"Error fetching search results: {str(e)}")
        return []


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

        response = requests.get(result.url, timeout=5, headers=headers)
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
            h.single_line_break = False  # Use two line breaks to create a new paragraph
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
            logging.warning(
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
        if len(full_content) > 8000:
            full_content = full_content[:8000] + "... [content truncated]"

        result.content = full_content
        return result
    except requests.RequestException as e:
        result.content = f"Error: Failed to retrieve the webpage. {str(e)}"
        return result
    except Exception as e:
        result.content = f"Error: Failed to scrape content. {str(e)}"
        return result


def process_search_results(results: List[APISearchResult]) -> List[SearchResult]:
    """
    Processes API search results into SearchResult objects with scraped content.

    Args:
        results: List of APISearchResult objects from search APIs

    Returns:
        List of SearchResult objects with scraped content
    """
    processed_results = []

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


def fetch_duckduckgo_search_results(
    query: str, max_results: int = 3
) -> List[APISearchResult]:
    """
    Fetches search results from DuckDuckGo as a free fallback.

    Args:
        query: The search query
        max_results: Maximum number of results to return

    Returns:
        A list of APISearchResult objects from DuckDuckGo
    """
    if not DDGS:
        logging.error("DuckDuckGo search not available (library not installed)")
        return []

    try:
        logging.info(f"Using DuckDuckGo fallback search for: {query}")

        with DDGS() as ddgs:
            # Get search results from DuckDuckGo
            results = []
            search_results = ddgs.text(query, max_results=max_results)

            for result in search_results:
                # Convert DuckDuckGo result format to APISearchResult
                results.append(
                    APISearchResult(
                        title=result.get("title", "Untitled"),
                        link=result.get("href", ""),
                        snippet=result.get("body", ""),
                    )
                )

            logging.info(f"DuckDuckGo returned {len(results)} results")
            return results

    except Exception as e:
        logging.error(f"Error fetching DuckDuckGo search results: {str(e)}")
        return []


# Create a search tool
@mcp_server.tool(
    name="search",
    description="Search the web for information using Serper API or DuckDuckGo fallback",
)
async def search_tool(query: str, ctx=None) -> dict:
    """Search the web for information on a given query.

    Returns:
        Dict representation of SearchResponse model
    """
    logging.info(f"Processing search request: {query}")

    results = []
    search_source = "Unknown"

    # Try Serper API first if key is available
    if SERPER_API_KEY:
        logging.info("Using Serper API for search")
        search_source = "Serper API"
        results = fetch_search_results(query, SERPER_API_KEY)

    # Fall back to DuckDuckGo if no API key or no results from Serper
    if not results:
        if not SERPER_API_KEY:
            logging.info("No Serper API key configured, using DuckDuckGo fallback")
        else:
            logging.warning("No results from Serper API, trying DuckDuckGo fallback")

        search_source = "DuckDuckGo (free fallback)"
        results = fetch_duckduckgo_search_results(query)

    # Check if we got any results
    if not results:
        logging.warning(f"No search results found for query: {query}")
        response = SearchResponse(
            query=query,
            search_source=search_source,
            results=[],
            error="No search results found from any source.",
        )
        return response.model_dump()

    # Process the results
    processed_results = process_search_results(results)

    # Return formatted results as SearchResponse
    response = SearchResponse(
        query=query,
        search_source=search_source,
        results=processed_results,
    )
    return response.model_dump()


# Create a simple health check tool
@mcp_server.tool(name="health_check", description="Check the health of the server")
async def health_check() -> dict:
    """Check the health of the server.

    Returns:
        Dict representation of HealthCheckResponse model
    """
    response = HealthCheckResponse(status="healthy", service="webcat")
    return response.model_dump()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting FastMCP server on port {port}")

    # Run the server with SSE transport for LiteLLM compatibility
    mcp_server.run(
        transport="sse",
        host="0.0.0.0",
        port=port,
        path="/mcp",  # Explicit path for MCP endpoint
    )
