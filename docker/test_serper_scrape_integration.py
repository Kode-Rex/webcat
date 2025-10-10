#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Integration test for Serper scrape API functionality."""

import os
import sys

# Add docker directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.serper_client import scrape_webpage  # noqa: E402
from models.domain.search_result import SearchResult  # noqa: E402
from services.content_scraper import scrape_search_result  # noqa: E402


def test_serper_scrape_client():
    """Test the Serper scrape client directly."""
    api_key = os.environ.get("SERPER_API_KEY", "")

    if not api_key:
        print("⚠️  SERPER_API_KEY not set - skipping Serper scrape test")
        return True

    print("🧪 Testing Serper scrape client...")

    # Test with a simple, reliable URL
    test_url = "https://example.com"

    try:
        result = scrape_webpage(test_url, api_key)

        if result is None:
            print(f"❌ Serper scrape returned None for {test_url}")
            return False

        if len(result) < 10:
            print(
                f"❌ Serper scrape returned suspiciously short content: {len(result)} chars"
            )
            return False

        print(f"✅ Serper scrape client working! Returned {len(result)} chars")
        print(f"📄 Preview: {result[:200]}...")
        return True

    except Exception as e:
        print(f"❌ Serper scrape client failed: {str(e)}")
        return False


def test_content_scraper_with_serper():
    """Test the content scraper service with Serper integration."""
    api_key = os.environ.get("SERPER_API_KEY", "")

    if not api_key:
        print("⚠️  SERPER_API_KEY not set - skipping content scraper test")
        return True

    print("\n🧪 Testing content scraper with Serper integration...")

    # Create a test search result
    test_result = SearchResult(
        title="Example Domain",
        url="https://example.com",
        snippet="This domain is for use in illustrative examples",
    )

    try:
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

        print(f"✅ Content scraper working! Returned {len(scraped.content)} chars")
        print(f"📄 Preview:\n{scraped.content[:300]}...")
        return True

    except Exception as e:
        print(f"❌ Content scraper failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_fallback_to_trafilatura():
    """Test that Trafilatura fallback works when Serper is not available."""
    print("\n🧪 Testing Trafilatura fallback (without Serper key)...")

    # Temporarily remove API key
    original_key = os.environ.get("SERPER_API_KEY")
    if original_key:
        os.environ["SERPER_API_KEY"] = ""

    try:
        test_result = SearchResult(
            title="Example Domain",
            url="https://example.com",
            snippet="This domain is for use in illustrative examples",
        )

        scraped = scrape_search_result(test_result)

        if not scraped.content:
            print("❌ Trafilatura fallback returned empty content")
            return False

        if "Error:" in scraped.content:
            print(f"❌ Trafilatura fallback returned error: {scraped.content}")
            return False

        print(f"✅ Trafilatura fallback working! Returned {len(scraped.content)} chars")
        return True

    except Exception as e:
        print(f"❌ Trafilatura fallback failed: {str(e)}")
        return False
    finally:
        # Restore API key
        if original_key:
            os.environ["SERPER_API_KEY"] = original_key


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("🚀 Serper Scrape Integration Tests")
    print("=" * 60)

    results = []

    # Test 1: Serper scrape client
    results.append(("Serper scrape client", test_serper_scrape_client()))

    # Test 2: Content scraper with Serper
    results.append(("Content scraper with Serper", test_content_scraper_with_serper()))

    # Test 3: Trafilatura fallback
    results.append(("Trafilatura fallback", test_fallback_to_trafilatura()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
