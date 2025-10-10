#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Simple MCP client to test WebCat tools via SSE transport."""

import asyncio
import os

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables from .env file
load_dotenv()


async def test_search():
    """Test the search tool via SSE transport."""
    # Get optional bearer token from environment
    api_key = os.environ.get("WEBCAT_API_KEY", "")

    # Set up headers for authentication if needed
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        print("🔐 Using bearer token authentication")
    else:
        print("🔓 No authentication (WEBCAT_API_KEY not set)")

    # Connect to the FastMCP SSE endpoint
    url = "http://localhost:8000/mcp/sse"

    print(f"📡 Connecting to {url}...")

    async with sse_client(url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to MCP server")

            # List available tools
            tools = await session.list_tools()
            print("\n🛠️  Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call search tool
            print("\n🔍 Testing search tool with query 'test'...")
            result = await session.call_tool("search", arguments={"query": "test"})

            print("\n📊 Search result:")
            print(f"  Content length: {len(str(result.content))}")
            print(
                f"  Is error: {result.isError if hasattr(result, 'isError') else 'N/A'}"
            )
            if hasattr(result, "content") and result.content:
                # Print first 200 chars of content
                content_preview = str(result.content)[:200]
                print(f"  Preview: {content_preview}...")


if __name__ == "__main__":
    print("🐱 WebCat MCP Client Test\n")
    try:
        asyncio.run(test_search())
        print("\n✨ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
