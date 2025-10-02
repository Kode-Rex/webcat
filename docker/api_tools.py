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
            Dict representation of APISearchToolResponse model
        """
        try:
            logger.info(
                f"Processing search request: {query} (max {max_results} results)"
            )

            # Call the existing search function
            if "search" in webcat_functions:
                result = await webcat_functions["search"](query)

                # Limit results if specified
                note = ""
                results = result.get("results", [])
                if results and len(results) > max_results:
                    results = results[:max_results]
                    note = f"Results limited to {max_results} items"

                response = APISearchToolResponse(
                    success=True,
                    query=query,
                    max_results=max_results,
                    search_source=result.get("search_source", "Unknown"),
                    results=results,
                    total_found=len(results),
                    note=note,
                )
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
            from mcp_server import SearchResult, scrape_search_result

            # Create a SearchResult object for scraping
            search_result = SearchResult(
                title="Direct URL Scrape",
                url=url,
                snippet="Content scraped directly from URL",
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
            import os

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


def create_webcat_functions() -> Dict[str, Any]:
    """Create a dictionary of WebCat functions for the tools to use."""

    # Import the existing functions from the main server
    from mcp_server import (
        SERPER_API_KEY,
        fetch_duckduckgo_search_results,
        fetch_search_results,
        process_search_results,
    )

    async def search_function(query: str) -> Dict[str, Any]:
        """Wrapper for the search functionality."""
        import asyncio

        results = []
        search_source = "Unknown"

        try:
            # Try Serper API first if key is available
            if SERPER_API_KEY:
                logger.info("Using Serper API for search")
                search_source = "Serper API"
                # Run the synchronous function in a thread pool
                results = await asyncio.get_event_loop().run_in_executor(
                    None, fetch_search_results, query, SERPER_API_KEY
                )

            # Fall back to DuckDuckGo if no API key or no results from Serper
            if not results:
                if not SERPER_API_KEY:
                    logger.info(
                        "No Serper API key configured, using DuckDuckGo fallback"
                    )
                else:
                    logger.warning(
                        "No results from Serper API, trying DuckDuckGo fallback"
                    )

                search_source = "DuckDuckGo (free fallback)"
                # Run the synchronous function in a thread pool
                results = await asyncio.get_event_loop().run_in_executor(
                    None, fetch_duckduckgo_search_results, query
                )

            # Check if we got any results
            if not results:
                logger.warning(f"No search results found for query: {query}")
                return {
                    "error": "No search results found from any source.",
                    "query": query,
                    "search_source": search_source,
                }

            # Process the results in thread pool (since it involves web scraping)
            processed_results = await asyncio.get_event_loop().run_in_executor(
                None, process_search_results, results
            )

            # Return formatted results
            return {
                "query": query,
                "search_source": search_source,
                "results": [result.model_dump() for result in processed_results],
            }

        except Exception as e:
            logger.error(f"Error in search function: {str(e)}")
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "search_source": search_source,
            }

    async def health_check_function() -> Dict[str, Any]:
        """Wrapper for the health check functionality."""
        import time

        return {"status": "healthy", "service": "webcat", "timestamp": time.time()}

    return {"search": search_function, "health_check": health_check_function}
