"""API tools module for FastMCP WebCat integration."""

import logging
from typing import TYPE_CHECKING, Dict, Any, List, Optional
from fastmcp import FastMCP
import asyncio

if TYPE_CHECKING:
    from .webcat_client import WebCatClient

logger = logging.getLogger(__name__)

def setup_webcat_tools(mcp: FastMCP, webcat_functions: Dict[str, Any]):
    """Setup webcat tools for HTTP/SSE API access"""
    
    @mcp.tool(
        name="search",
        description="Search the web for information using Serper API or DuckDuckGo fallback"
    )
    async def search_tool(query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web for information on a given query."""
        try:
            logger.info(f"Processing search request: {query} (max {max_results} results)")
            
            # Call the existing search function
            if 'search' in webcat_functions:
                result = await webcat_functions['search'](query)
                
                # Limit results if specified
                if result.get('results') and len(result['results']) > max_results:
                    result['results'] = result['results'][:max_results]
                    result['note'] = f"Results limited to {max_results} items"
                
                return {
                    "success": True,
                    "query": query,
                    "max_results": max_results,
                    "search_source": result.get('search_source', 'Unknown'),
                    "results": result.get('results', []),
                    "total_found": len(result.get('results', [])),
                    "note": result.get('note', '')
                }
            else:
                return {"error": "Search function not available"}
                
        except Exception as e:
            logger.error(f"Error in search tool: {str(e)}")
            return {"error": str(e), "query": query}
    
    @mcp.tool(
        name="health_check",
        description="Check the health status of the WebCat server"
    )
    async def health_check_tool() -> Dict[str, Any]:
        """Check the health of the WebCat server."""
        try:
            logger.info("Processing health check request")
            
            # Call the existing health check function
            if 'health_check' in webcat_functions:
                result = await webcat_functions['health_check']()
                return {
                    "success": True,
                    "status": result.get('status', 'unknown'),
                    "service": result.get('service', 'webcat'),
                    "timestamp": result.get('timestamp', 'unknown')
                }
            else:
                return {
                    "success": True,
                    "status": "healthy",
                    "service": "webcat",
                    "message": "Basic health check passed"
                }
                
        except Exception as e:
            logger.error(f"Error in health check tool: {str(e)}")
            return {"error": str(e), "status": "unhealthy"}
    
    @mcp.tool(
        name="scrape_url",
        description="Scrape and extract content from a specific URL"
    )
    async def scrape_url_tool(url: str) -> Dict[str, Any]:
        """Scrape content from a specific URL and convert to markdown."""
        try:
            logger.info(f"Processing scrape request for URL: {url}")
            
            # Import the scraping functionality from the main server
            from mcp_server import scrape_search_result, SearchResult
            
            # Create a SearchResult object for scraping
            search_result = SearchResult(
                title="Direct URL Scrape",
                url=url,
                snippet="Content scraped directly from URL"
            )
            
            # Scrape the content
            scraped_result = scrape_search_result(search_result)
            
            return {
                "success": True,
                "url": url,
                "title": scraped_result.title,
                "content": scraped_result.content,
                "content_length": len(scraped_result.content)
            }
                
        except Exception as e:
            logger.error(f"Error in scrape URL tool: {str(e)}")
            return {"error": str(e), "url": url}
    
    @mcp.tool(
        name="get_server_info",
        description="Get information about the WebCat server configuration and capabilities"
    )
    async def get_server_info_tool() -> Dict[str, Any]:
        """Get information about the WebCat server."""
        try:
            import os
            
            logger.info("Processing server info request")
            
            return {
                "success": True,
                "service": "WebCat MCP Server",
                "version": "2.2.0",
                "capabilities": [
                    "Web search with Serper API",
                    "DuckDuckGo fallback search",
                    "Content extraction and scraping",
                    "Markdown conversion",
                    "FastMCP protocol support",
                    "SSE streaming"
                ],
                "configuration": {
                    "serper_api_configured": bool(os.environ.get("SERPER_API_KEY")),
                    "duckduckgo_available": True,  # Always available in our setup
                    "port": int(os.environ.get("PORT", 8000)),
                    "log_level": os.environ.get("LOG_LEVEL", "INFO")
                },
                "endpoints": {
                    "main_mcp": "/mcp",
                    "sse_demo": "/sse",
                    "health": "/health",
                    "demo_client": "/client"
                }
            }
                
        except Exception as e:
            logger.error(f"Error in server info tool: {str(e)}")
            return {"error": str(e)}

def create_webcat_functions() -> Dict[str, Any]:
    """Create a dictionary of WebCat functions for the tools to use."""
    
    # Import the existing functions from the main server
    from mcp_server import (
        fetch_search_results, 
        fetch_duckduckgo_search_results,
        process_search_results,
        SERPER_API_KEY
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
                    logger.info("No Serper API key configured, using DuckDuckGo fallback")
                else:
                    logger.warning("No results from Serper API, trying DuckDuckGo fallback")
                
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
                    "search_source": search_source
                }
            
            # Process the results in thread pool (since it involves web scraping)
            processed_results = await asyncio.get_event_loop().run_in_executor(
                None, process_search_results, results
            )
            
            # Return formatted results
            return {
                "query": query,
                "search_source": search_source,
                "results": [result.model_dump() for result in processed_results]
            }
            
        except Exception as e:
            logger.error(f"Error in search function: {str(e)}")
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "search_source": search_source
            }
    
    async def health_check_function() -> Dict[str, Any]:
        """Wrapper for the health check functionality."""
        import time
        return {
            "status": "healthy", 
            "service": "webcat",
            "timestamp": time.time()
        }
    
    return {
        "search": search_function,
        "health_check": health_check_function
    }
