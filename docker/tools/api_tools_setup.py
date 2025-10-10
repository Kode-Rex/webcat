# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Setup functions for API tools in FastMCP WebCat integration."""

import logging
import os
import time
from typing import Any, Dict

from fastmcp import Context, FastMCP

from constants import CAPABILITIES, SERVICE_NAME, VERSION
from models.api_responses import (
    APIHealthCheckResponse,
    APIScrapeResponse,
    APISearchToolResponse,
    APIServerInfoResponse,
)
from models.search_result import SearchResult
from services.content_scraper import scrape_search_result
from services.search_orchestrator import execute_search
from utils.auth import validate_bearer_token

logger = logging.getLogger(__name__)


def setup_search_tool(mcp: FastMCP, search_func):
    """Setup search tool for MCP server."""

    @mcp.tool(
        name="search",
        description="Search the web for information using Serper API or DuckDuckGo fallback",
    )
    async def search_tool(query: str, ctx: Context, max_results: int = 5) -> dict:
        """Search the web for information on a given query."""
        try:
            # Validate authentication if WEBCAT_API_KEY is set
            is_valid, error_msg = validate_bearer_token(ctx)
            if not is_valid:
                logger.warning(f"Authentication failed: {error_msg}")
                response = APISearchToolResponse(
                    success=False,
                    query=query,
                    max_results=max_results,
                    search_source="none",
                    results=[],
                    total_found=0,
                    error=error_msg,
                )
                return response.model_dump()

            logger.info(
                f"Processing search request: {query} (max {max_results} results)"
            )

            result: dict = await search_func(query)

            # Limit results if specified
            note: str = ""
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


def setup_health_check_tool(mcp: FastMCP, health_func):
    """Setup health check tool for MCP server."""

    @mcp.tool(
        name="health_check", description="Check the health status of the WebCat server"
    )
    async def health_check_tool() -> dict:
        """Check the health of the WebCat server."""
        try:
            logger.info("Processing health check request")

            if health_func:
                result = await health_func()
                response = APIHealthCheckResponse(
                    success=True,
                    status=result.get("status", "unknown"),
                    service=result.get("service", "webcat"),
                )
            else:
                response = APIHealthCheckResponse(
                    success=True, status="healthy", service="webcat"
                )
            return response.model_dump()

        except Exception as e:
            logger.error(f"Error in health check tool: {str(e)}")
            response = APIHealthCheckResponse(
                success=False, status="unhealthy", service="webcat", error=str(e)
            )
            return response.model_dump()


def setup_scrape_tool(mcp: FastMCP):
    """Setup URL scraping tool for MCP server."""

    @mcp.tool(
        name="scrape_url", description="Scrape and extract content from a specific URL"
    )
    async def scrape_url_tool(url: str) -> dict:
        """Scrape content from a specific URL and convert to markdown."""
        try:
            logger.info(f"Processing scrape request for URL: {url}")

            # Create a SearchResult object for scraping
            search_result = SearchResult(title="", url=url, snippet="")

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
                success=False, url=url, title="", content="", error=str(e)
            )
            return response.model_dump()


def setup_server_info_tool(mcp: FastMCP):
    """Setup server info tool for MCP server."""

    @mcp.tool(
        name="get_server_info",
        description="Get information about the WebCat server configuration and capabilities",
    )
    async def get_server_info_tool() -> dict:
        """Get information about the WebCat server."""
        try:
            logger.info("Processing server info request")

            response = APIServerInfoResponse(
                success=True,
                version=VERSION,
                server=SERVICE_NAME,
                features=CAPABILITIES,
            )
            return response.model_dump()

        except Exception as e:
            logger.error(f"Error in server info tool: {str(e)}")
            response = APIServerInfoResponse(
                success=False,
                version="unknown",
                server=SERVICE_NAME,
                features=[],
                error=str(e),
            )
            return response.model_dump()


def setup_webcat_tools(mcp: FastMCP, webcat_functions: Dict[str, Any]):
    """Setup all WebCat tools for HTTP/SSE API access.

    Args:
        mcp: FastMCP server instance
        webcat_functions: Dictionary of WebCat functions
    """
    setup_search_tool(mcp, webcat_functions.get("search"))
    setup_health_check_tool(mcp, webcat_functions.get("health_check"))
    setup_scrape_tool(mcp)
    setup_server_info_tool(mcp)


def create_webcat_functions() -> Dict[str, Any]:
    """Create a dictionary of WebCat functions for the tools to use."""
    SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

    async def search_function(query: str) -> Dict[str, Any]:
        """Wrapper for the search functionality."""
        return await execute_search(query, SERPER_API_KEY)

    async def health_check_function() -> Dict[str, Any]:
        """Wrapper for the health check functionality."""
        return {"status": "healthy", "service": "webcat", "timestamp": time.time()}

    return {"search": search_function, "health_check": health_check_function}
