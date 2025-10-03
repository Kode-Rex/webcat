# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""API tools module for FastMCP WebCat integration."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# Response models for API tools
class APISearchToolResponse(BaseModel):
    """Response from API search tool with additional metadata."""

    success: bool
    query: str
    max_results: int
    search_source: str
    results: List[Dict[str, Any]]  # SearchResult dicts
    total_found: int
    note: str = ""
    error: Optional[str] = None


class APIHealthCheckResponse(BaseModel):
    """Response from API health check tool."""

    success: bool
    status: str
    service: str
    error: Optional[str] = None


class APIServerInfoResponse(BaseModel):
    """Response from API server info tool."""

    success: bool
    version: str
    server: str
    features: List[str]
    error: Optional[str] = None


class APIScrapeResponse(BaseModel):
    """Response from API scrape tool."""

    success: bool
    url: str
    title: str
    content: str
    error: Optional[str] = None


def setup_webcat_tools(mcp: FastMCP, webcat_functions: Dict[str, Any]):
    """Setup webcat tools for HTTP/SSE API access"""

    @mcp.tool(
        name="search",
        description="Search the web for information using Serper API or DuckDuckGo fallback",
    )
    async def search_tool(query: str, max_results: int = 5) -> dict:
        """Search the web for information on a given query.

        Returns:
            Dict representation of APISearchToolResponse model (for MCP JSON serialization)
        """
        try:
            logger.info(
                f"Processing search request: {query} (max {max_results} results)"
            )

            # Call the existing search function
            if "search" in webcat_functions:
                result: dict = await webcat_functions["search"](query)

                # Limit results if specified
                note: str = ""
                results: List[Dict[str, Any]] = result.get("results", [])
                if results and len(results) > max_results:
                    results = results[:max_results]
                    note = f"Results limited to {max_results} items"

                # Build typed response
                response = APISearchToolResponse(
                    success=True,
                    query=query,
                    max_results=max_results,
                    search_source=result.get("search_source", "Unknown"),
                    results=results,
                    total_found=len(results),
                    note=note,
                )
                # Only convert to dict at MCP boundary for JSON serialization
                return response.model_dump()
            else:
                response = APISearchToolResponse(
                    success=False,
                    query=query,
                    max_results=max_results,
                    search_source="Unknown",
                    results=[],
                    total_found=0,
                    error="Search function not available",
                )
                return response.model_dump()

        except Exception as e:
            logger.error(f"Error in search tool: {str(e)}")
            response = APISearchToolResponse(
                success=False,
                query=query,
                max_results=max_results,
                search_source="Unknown",
                results=[],
                total_found=0,
                error=str(e),
            )
            return response.model_dump()

    @mcp.tool(
        name="health_check", description="Check the health status of the WebCat server"
    )
    async def health_check_tool() -> dict:
        """Check the health of the WebCat server.

        Returns:
            Dict representation of APIHealthCheckResponse model
        """
        try:
            logger.info("Processing health check request")

            # Call the existing health check function
            if "health_check" in webcat_functions:
                result = await webcat_functions["health_check"]()
                response = APIHealthCheckResponse(
                    success=True,
                    status=result.get("status", "unknown"),
                    service=result.get("service", "webcat"),
                )
                return response.model_dump()
            else:
                response = APIHealthCheckResponse(
                    success=True,
                    status="healthy",
                    service="webcat",
                )
                return response.model_dump()

        except Exception as e:
            logger.error(f"Error in health check tool: {str(e)}")
            response = APIHealthCheckResponse(
                success=False,
                status="unhealthy",
                service="webcat",
                error=str(e),
            )
            return response.model_dump()

    @mcp.tool(
        name="scrape_url", description="Scrape and extract content from a specific URL"
    )
    async def scrape_url_tool(url: str) -> dict:
        """Scrape content from a specific URL and convert to markdown.

        Returns:
            Dict representation of APIScrapeResponse model
        """
        try:
            logger.info(f"Processing scrape request for URL: {url}")

            # Import the scraping functionality from the main server
            from models.search_result import SearchResult
            from services.content_scraper import scrape_search_result

            # Create a SearchResult object for scraping
            # Title will be extracted from the page during scraping
            search_result = SearchResult(
                title="",
                url=url,
                snippet="",
            )

            # Scrape the content
            scraped_result = scrape_search_result(search_result)

            response = APIScrapeResponse(
                success=True,
                url=url,
                title=scraped_result.title,
                content=scraped_result.content,
            )
            return response.model_dump()

        except Exception as e:
            logger.error(f"Error in scrape URL tool: {str(e)}")
            response = APIScrapeResponse(
                success=False,
                url=url,
                title="",
                content="",
                error=str(e),
            )
            return response.model_dump()

    @mcp.tool(
        name="get_server_info",
        description="Get information about the WebCat server configuration and capabilities",
    )
    async def get_server_info_tool() -> dict:
        """Get information about the WebCat server.

        Returns:
            Dict representation of APIServerInfoResponse model
        """
        try:
            logger.info("Processing server info request")

            features = [
                "Web search with Serper API",
                "DuckDuckGo fallback search",
                "Content extraction and scraping",
                "Markdown conversion",
                "FastMCP protocol support",
                "SSE streaming",
            ]

            response = APIServerInfoResponse(
                success=True,
                version="2.2.0",
                server="WebCat MCP Server",
                features=features,
            )
            return response.model_dump()

        except Exception as e:
            logger.error(f"Error in server info tool: {str(e)}")
            response = APIServerInfoResponse(
                success=False,
                version="unknown",
                server="WebCat MCP Server",
                features=[],
                error=str(e),
            )
            return response.model_dump()


async def _fetch_with_serper(query: str, api_key: str):
    """Fetch search results using Serper API.

    Args:
        query: Search query
        api_key: Serper API key

    Returns:
        Tuple of (results, search_source)
    """
    import asyncio

    from clients.serper_client import fetch_search_results

    logger.info("Using Serper API for search")
    results = await asyncio.get_event_loop().run_in_executor(
        None, fetch_search_results, query, api_key
    )
    return results, "Serper API"


async def _fetch_with_duckduckgo(query: str, has_api_key: bool):
    """Fetch search results using DuckDuckGo.

    Args:
        query: Search query
        has_api_key: Whether Serper API key was configured

    Returns:
        Tuple of (results, search_source)
    """
    import asyncio

    from clients.duckduckgo_client import fetch_duckduckgo_search_results

    if not has_api_key:
        logger.info("No Serper API key configured, using DuckDuckGo fallback")
    else:
        logger.warning("No results from Serper API, trying DuckDuckGo fallback")

    results = await asyncio.get_event_loop().run_in_executor(
        None, fetch_duckduckgo_search_results, query
    )
    return results, "DuckDuckGo (free fallback)"


def _format_no_results_error(query: str, search_source: str) -> dict:
    """Format error response for no results.

    Args:
        query: Search query
        search_source: Source that was used

    Returns:
        Error dictionary
    """
    return {
        "error": "No search results found from any source.",
        "query": query,
        "search_source": search_source,
    }


def _format_search_error(error: str, query: str, search_source: str) -> dict:
    """Format error response for search failure.

    Args:
        error: Error message
        query: Search query
        search_source: Source that was attempted

    Returns:
        Error dictionary
    """
    return {
        "error": f"Search failed: {error}",
        "query": query,
        "search_source": search_source,
    }


async def _process_and_format_results(results, query: str, search_source: str):
    """Process search results and format response.

    Args:
        results: Raw search results
        query: Search query
        search_source: Source of results

    Returns:
        Formatted results dictionary
    """
    import asyncio

    from services.search_processor import process_search_results

    processed_results = await asyncio.get_event_loop().run_in_executor(
        None, process_search_results, results
    )

    return {
        "query": query,
        "search_source": search_source,
        "results": [result.model_dump() for result in processed_results],
    }


def create_webcat_functions() -> Dict[str, Any]:
    """Create a dictionary of WebCat functions for the tools to use."""

    # Import SERPER_API_KEY from config
    import os

    SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

    async def search_function(query: str) -> Dict[str, Any]:
        """Wrapper for the search functionality."""
        results = []
        search_source = "Unknown"

        try:
            # Try Serper API first if key is available
            if SERPER_API_KEY:
                results, search_source = await _fetch_with_serper(query, SERPER_API_KEY)

            # Fall back to DuckDuckGo if no API key or no results from Serper
            if not results:
                results, search_source = await _fetch_with_duckduckgo(
                    query, bool(SERPER_API_KEY)
                )

            # Check if we got any results
            if not results:
                logger.warning(f"No search results found for query: {query}")
                return _format_no_results_error(query, search_source)

            # Process and format results
            return await _process_and_format_results(results, query, search_source)

        except Exception as e:
            logger.error(f"Error in search function: {str(e)}")
            return _format_search_error(str(e), query, search_source)

    async def health_check_function() -> Dict[str, Any]:
        """Wrapper for the health check functionality."""
        import time

        return {"status": "healthy", "service": "webcat", "timestamp": time.time()}

    return {"search": search_function, "health_check": health_check_function}
