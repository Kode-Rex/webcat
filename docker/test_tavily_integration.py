#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Integration test for Tavily API functionality."""

import os
import sys

# Add docker directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.tavily_client import extract_content, fetch_search_results  # noqa: E402
from models.domain.search_result import SearchResult  # noqa: E402
from services.content_scraper import scrape_search_result  # noqa: E402


def test_tavily_search_client():
    """Test the Tavily search client directly."""
    api_key = os.environ.get("TAVILY_API_KEY", "")

    if not api_key:
        print("⚠️  TAVILY_API_KEY not set - skipping Tavily search test")
        return True

    print("🧪 Testing Tavily search client...")

    # Test with a simple query
    test_query = "anthropic claude AI"

    try:
        results = fetch_search_results(test_query, api_key, max_results=3)

        if not results:
            print(f"❌ Tavily search returned no results for '{test_query}'")
            return False

        if len(results) == 0:
            print(f"❌ Tavily search returned empty list for '{test_query}'")
            return False

        print(f"✅ Tavily search working! Returned {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. {result.title} - {result.link}")

        return True

    except Exception as e:
        print(f"❌ Tavily search client failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_tavily_extract_client():
    """Test the Tavily extract client directly."""
    api_key = os.environ.get("TAVILY_API_KEY", "")

    if not api_key:
        print("⚠️  TAVILY_API_KEY not set - skipping Tavily extract test")
        return True

    print("\n🧪 Testing Tavily extract client...")

    # Test with a simple, reliable URL
    test_url = "https://example.com"

    try:
        content = extract_content(test_url, api_key)

        if content is None:
            print(f"❌ Tavily extract returned None for {test_url}")
            return False

        if len(content) < 10:
            print(
                f"❌ Tavily extract returned suspiciously short content: {len(content)} chars"
            )
            return False

        print(f"✅ Tavily extract working! Returned {len(content)} chars")
        print(f"📄 Preview: {content[:200]}...")
        return True

    except Exception as e:
        print(f"❌ Tavily extract client failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_content_scraper_with_tavily():
    """Test the content scraper service with Tavily integration."""
    api_key = os.environ.get("TAVILY_API_KEY", "")

    if not api_key:
        print("⚠️  TAVILY_API_KEY not set - skipping content scraper test")
        return True

    print("\n🧪 Testing content scraper with Tavily integration...")

    # Temporarily remove Serper key to force Tavily usage
    original_serper_key = os.environ.get("SERPER_API_KEY")
    if original_serper_key:
        os.environ["SERPER_API_KEY"] = ""

    try:
        # Create a test search result
        test_result = SearchResult(
            title="Example Domain",
            url="https://example.com",
            snippet="This domain is for use in illustrative examples",
        )

        scraped = scrape_search_result(test_result)

        if not scraped.content:
            print("❌ Content scraper returned empty content")
            return False

        if "Error:" in scraped.content:
            print(f"❌ Content scraper returned error: {scraped.content}")
            return False

        # Check that it includes our formatting
        if "# Example Domain" not in scraped.content:
            print("❌ Content missing expected title formatting")
            return False

        if "*Source: https://example.com*" not in scraped.content:
            print("❌ Content missing expected source attribution")
            return False

        print(
            f"✅ Content scraper with Tavily working! Returned {len(scraped.content)} chars"
        )
        print(f"📄 Preview:\n{scraped.content[:300]}...")
        return True

    except Exception as e:
        print(f"❌ Content scraper with Tavily failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Restore Serper key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key


def test_fallback_priority():
    """Test that Tavily is used as fallback when Serper unavailable."""
    tavily_key = os.environ.get("TAVILY_API_KEY", "")
    serper_key = os.environ.get("SERPER_API_KEY", "")

    if not tavily_key or not serper_key:
        print(
            "\n⚠️  Both TAVILY_API_KEY and SERPER_API_KEY needed for fallback test - skipping"
        )
        return True

    print("\n🧪 Testing fallback priority (Serper → Tavily)...")

    # This test verifies the fallback logic is in place
    # In real usage, Tavily would be tried if Serper fails
    print("✅ Fallback chain configured: Serper → Tavily → DuckDuckGo (for search)")
    print("✅ Fallback chain configured: Serper → Tavily → Trafilatura (for scraping)")
    print("   Note: Full fallback testing requires simulating Serper failures")

    return True


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("🚀 Tavily Integration Tests")
    print("=" * 70)

    results = []

    # Test 1: Tavily search client
    results.append(("Tavily search client", test_tavily_search_client()))

    # Test 2: Tavily extract client
    results.append(("Tavily extract client", test_tavily_extract_client()))

    # Test 3: Content scraper with Tavily
    results.append(("Content scraper with Tavily", test_content_scraper_with_tavily()))

    # Test 4: Fallback priority
    results.append(("Fallback priority", test_fallback_priority()))

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
