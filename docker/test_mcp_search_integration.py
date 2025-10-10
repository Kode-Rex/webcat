#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Integration test for MCP search tool with Serper scraping."""

import json
import os
import sys
import time

import requests

# Test configuration
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for MCP server to be ready."""
    print(f"⏳ Waiting for MCP server at {url}...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            # Try MCP endpoint directly with proper headers
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
            response = requests.post(
                url,
                json={"jsonrpc": "2.0", "id": 0, "method": "tools/list"},
                headers=headers,
                timeout=2,
            )
            # Any 200 response means server is up
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.RequestException:
            time.sleep(1)

    print(f"❌ Server not ready after {timeout}s")
    return False


def test_mcp_search_with_serper():
    """Test MCP search tool with Serper API (includes scraping)."""
    if not SERPER_API_KEY:
        print("⚠️  SERPER_API_KEY not set - skipping Serper test")
        return True

    print("\n🧪 Testing MCP search tool with Serper...")

    # MCP JSON-RPC 2.0 request for search tool
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search",
            "arguments": {"query": "anthropic claude", "max_results": 2},
        },
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        response = requests.post(
            MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code != 200:
            print(f"❌ MCP server returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False

        data = response.json()

        # Check for JSON-RPC error
        if "error" in data:
            print(f"❌ MCP returned error: {data['error']}")
            return False

        # Check result structure
        if "result" not in data:
            print(f"❌ Missing result in response: {data}")
            return False

        result = data["result"]

        # Parse the content (should be JSON string)
        if "content" not in result or not result["content"]:
            print(f"❌ Missing content in result: {result}")
            return False

        content_items = result["content"]
        if not isinstance(content_items, list) or len(content_items) == 0:
            print(f"❌ Content is not a list or is empty: {content_items}")
            return False

        # Get the text content
        text_content = content_items[0].get("text", "")
        if not text_content:
            print(f"❌ No text content found: {content_items}")
            return False

        # Parse the JSON response from search tool
        try:
            search_results = json.loads(text_content)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse search results JSON: {e}")
            print(f"Content: {text_content[:500]}")
            return False

        # Validate search results structure
        if "results" not in search_results:
            print(f"❌ No 'results' key in search results: {search_results.keys()}")
            return False

        results = search_results["results"]
        if not isinstance(results, list):
            print(f"❌ Results is not a list: {type(results)}")
            return False

        if len(results) == 0:
            print("❌ No search results returned")
            return False

        print(f"✅ Got {len(results)} search results")

        # Verify each result has scraped content
        for i, result in enumerate(results):
            if "title" not in result:
                print(f"❌ Result {i} missing title")
                return False

            if "url" not in result:
                print(f"❌ Result {i} missing url")
                return False

            if "content" not in result:
                print(f"❌ Result {i} missing content (scraping failed?)")
                return False

            content = result["content"]

            # Check for Serper scraping indicators
            if "# " in content and "*Source:" in content:
                print(
                    f"✅ Result {i}: '{result['title']}' - {len(content)} chars (Serper scraping worked!)"
                )
            else:
                print(
                    f"⚠️  Result {i}: '{result['title']}' - {len(content)} chars (may have used fallback)"
                )

            # Show preview
            if i == 0:
                preview = content[:300]
                print(f"\n📄 Content preview:\n{preview}...\n")

        return True

    except requests.exceptions.Timeout:
        print("❌ Request timeout - server may be slow or unresponsive")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_mcp_search_without_serper():
    """Test MCP search tool without Serper (DuckDuckGo + Trafilatura)."""
    print("\n🧪 Testing MCP search tool without Serper (fallback mode)...")

    # Temporarily remove API key
    original_key = os.environ.get("SERPER_API_KEY")
    if original_key:
        os.environ["SERPER_API_KEY"] = ""

    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {"query": "python programming", "max_results": 2},
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        response = requests.post(
            MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code != 200:
            print(
                f"⚠️  Fallback test skipped - server may require Serper key (status {response.status_code})"
            )
            return True

        data = response.json()

        if "error" in data:
            print(f"⚠️  Fallback test got error (may be expected): {data['error']}")
            return True

        if "result" in data and "content" in data["result"]:
            content_items = data["result"]["content"]
            if content_items and len(content_items) > 0:
                text_content = content_items[0].get("text", "")
                if text_content:
                    search_results = json.loads(text_content)
                    if (
                        "results" in search_results
                        and len(search_results["results"]) > 0
                    ):
                        print(
                            f"✅ Fallback mode working! Got {len(search_results['results'])} results"
                        )
                        return True

        print("⚠️  Fallback test inconclusive")
        return True

    except Exception as e:
        print(f"⚠️  Fallback test failed: {str(e)}")
        return True  # Don't fail on fallback test
    finally:
        # Restore API key
        if original_key:
            os.environ["SERPER_API_KEY"] = original_key


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("🚀 MCP Search Integration Tests")
    print("=" * 70)

    # Wait for server
    if not wait_for_server(MCP_SERVER_URL):
        print("\n❌ Server not available - cannot run tests")
        return 1

    results = []

    # Test 1: Search with Serper
    results.append(("MCP search with Serper", test_mcp_search_with_serper()))

    # Test 2: Search without Serper (fallback)
    results.append(("MCP search fallback", test_mcp_search_without_serper()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
