# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Entry point for the WebCat server using FastMCP.

Type Safety Architecture:
-------------------------
This module uses Pydantic models for strong typing throughout:

1. **Internal Functions**: Return typed Pydantic models
   - fetch_search_results() -> List[APISearchResult]
   - process_search_results() -> List[SearchResult]
   - Full type safety, IDE autocomplete, mypy validation

2. **MCP Tool Functions**: Only convert to dict at the boundary
   - @mcp_server.tool() functions MUST return dict (MCP protocol requirement)
   - Internal logic uses typed models
   - Only call .model_dump() at return statement for JSON serialization

3. **Benefits**:
   - Type safety everywhere except MCP boundary
   - Pydantic validates data structure automatically
   - IDE provides full autocomplete
   - mypy catches type errors at development time

Example:
    # Internal function - returns typed model
    def fetch_results() -> List[APISearchResult]:
        return [APISearchResult(...)]

    # MCP tool - uses types internally, converts at boundary
    @mcp_server.tool()
    async def search_tool() -> dict:
        results: List[APISearchResult] = fetch_results()  # Typed!
        response = SearchResponse(results=results)        # Typed!
        return response.model_dump()                      # Dict for MCP
"""

import logging
import os
import tempfile
from typing import List

from dotenv import load_dotenv
from fastmcp import FastMCP

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


# Import models from dedicated modules
from models.api_search_result import APISearchResult
from models.error_response import ErrorResponse
from models.health_check_response import HealthCheckResponse
from models.search_response import SearchResponse
from models.search_result import SearchResult


# Configure API keys
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

logging.info(
    f"Using SERPER API key from environment: {'Set' if SERPER_API_KEY else 'Not set'}"
)

# Create FastMCP instance (no authentication required)
mcp_server = FastMCP("WebCat Search")


# Import client functions
from clients.duckduckgo_client import (
    fetch_duckduckgo_search_results as fetch_ddg_results,
)
from clients.serper_client import fetch_search_results

# Import service functions
from services.content_scraper import scrape_search_result
from services.search_processor import process_search_results


# Create a search tool
@mcp_server.tool(
    name="search",
    description="Search the web for information using Serper API or DuckDuckGo fallback",
)
async def search_tool(query: str, ctx=None) -> dict:
    """Search the web for information on a given query.

    Returns:
        Dict representation of SearchResponse model (for MCP JSON serialization)
    """
    logging.info(f"Processing search request: {query}")

    # Typed as List[APISearchResult] - holds raw API responses
    api_results: List[APISearchResult] = []
    search_source: str = "Unknown"

    # Try Serper API first if key is available
    if SERPER_API_KEY:
        logging.info("Using Serper API for search")
        search_source = "Serper API"
        api_results = fetch_search_results(query, SERPER_API_KEY)

    # Fall back to DuckDuckGo if no API key or no results from Serper
    if not api_results:
        if not SERPER_API_KEY:
            logging.info("No Serper API key configured, using DuckDuckGo fallback")
        else:
            logging.warning("No results from Serper API, trying DuckDuckGo fallback")

        search_source = "DuckDuckGo (free fallback)"
        api_results = fetch_ddg_results(query)

    # Check if we got any results
    if not api_results:
        logging.warning(f"No search results found for query: {query}")
        response = SearchResponse(
            query=query,
            search_source=search_source,
            results=[],
            error="No search results found from any source.",
        )
        # Only convert to dict at MCP boundary for JSON serialization
        return response.model_dump()

    # Process the results - typed as List[SearchResult]
    processed_results: List[SearchResult] = process_search_results(api_results)

    # Build typed response
    response = SearchResponse(
        query=query,
        search_source=search_source,
        results=processed_results,
    )
    # Only convert to dict at MCP boundary for JSON serialization
    return response.model_dump()


# Create a simple health check tool
@mcp_server.tool(name="health_check", description="Check the health of the server")
async def health_check() -> dict:
    """Check the health of the server.

    Returns:
        Dict representation of HealthCheckResponse model (for MCP JSON serialization)
    """
    # Build typed response
    response = HealthCheckResponse(status="healthy", service="webcat")
    # Only convert to dict at MCP boundary for JSON serialization
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
