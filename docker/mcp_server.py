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

from dotenv import load_dotenv
from fastmcp import FastMCP

from utils.logging_config import setup_logging

# Load environment variables FIRST before importing tools
load_dotenv()

# Set up logging
logger = setup_logging("webcat.log")

# Import tools AFTER loading .env so they can access environment variables
from tools.deep_research_tool import deep_research_tool  # noqa: E402
from tools.health_check_tool import health_check_tool  # noqa: E402
from tools.search_tool import search_tool  # noqa: E402

# Log configuration status
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
logging.info(
    f"SERPER API key: {'Set' if SERPER_API_KEY else 'Not set (using DuckDuckGo fallback)'}"
)
logging.info(
    f"PERPLEXITY API key: {'Set' if PERPLEXITY_API_KEY else 'Not set (deep_research tool unavailable)'}"
)


# Create FastMCP instance
mcp_server = FastMCP("WebCat Search")

# Register tools with MCP server
mcp_server.tool(
    name="search",
    description="Search the web for information using Serper API or DuckDuckGo fallback",
)(search_tool)

mcp_server.tool(
    name="deep_research",
    description=(
        "Perform comprehensive deep research on a topic using Perplexity AI. "
        "This tool performs dozens of searches, reads hundreds of sources, and "
        "synthesizes findings into a comprehensive report. Ideal for in-depth "
        "analysis and multi-source research. Takes 2-4 minutes to complete."
    ),
)(deep_research_tool)

mcp_server.tool(name="health_check", description="Check the health of the server")(
    health_check_tool
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(
        f"Starting FastMCP server on port {port} (no auth - use nginx proxy for auth)"
    )

    # Run the server with modern HTTP transport (Streamable HTTP with JSON-RPC 2.0)
    # NOTE: Authentication should be handled by reverse proxy (nginx) not in-app
    mcp_server.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp",  # Explicit path for MCP endpoint
    )
