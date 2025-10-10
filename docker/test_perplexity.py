#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Test script for Perplexity deep research functionality."""

import asyncio
import json
import os
import sys

# Add docker directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables before importing tools
from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from tools.deep_research_tool import deep_research_tool  # noqa: E402

# Check if API key is set
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

if not PERPLEXITY_API_KEY:
    print("❌ PERPLEXITY_API_KEY not set in .env file")
    print("Please add your API key to docker/.env:")
    print("PERPLEXITY_API_KEY=your_api_key_here")
    print("\nGet your API key at: https://www.perplexity.ai/settings/api")
    sys.exit(1)

print(f"✅ PERPLEXITY_API_KEY found: {PERPLEXITY_API_KEY[:8]}...")


async def test_deep_research():
    """Test the deep_research tool with a sample query."""
    print("\n" + "=" * 80)
    print("Testing Perplexity Deep Research Tool")
    print("=" * 80 + "\n")

    query = "What are the key differences between GPT-4 and Claude 3.5 Sonnet?"
    print(f"Query: {query}")
    print("Research Effort: low (for faster testing)")
    print("\nThis will take ~1 minute...\n")

    try:
        # Call the deep research tool
        result = await deep_research_tool(
            query=query,
            research_effort="low",  # Use low for faster testing
            max_results=5,
        )

        print("✅ Deep research completed!\n")
        print("=" * 80)
        print("RESULTS:")
        print("=" * 80 + "\n")

        # Pretty print the result
        print(json.dumps(result, indent=2))

        # Extract and display key information
        if "results" in result and result["results"]:
            first_result = result["results"][0]
            print("\n" + "=" * 80)
            print("FORMATTED RESEARCH REPORT:")
            print("=" * 80 + "\n")
            print(first_result.get("content", "No content"))

    except Exception as e:
        print(f"❌ Error during deep research: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_deep_research())
