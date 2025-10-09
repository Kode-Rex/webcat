#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Simple MCP client to test WebCat tools."""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_search():
    """Test the search tool."""
    # For SSE transport, we'd connect differently
    # For now, this is a reference for how MCP clients work

    server_params = StdioServerParameters(
        command="python", args=["mcp_server.py"], env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call search tool
            result = await session.call_tool("search", arguments={"query": "test"})
            print(f"\nSearch result: {result}")


if __name__ == "__main__":
    asyncio.run(test_search())
