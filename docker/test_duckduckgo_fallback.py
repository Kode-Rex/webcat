#!/usr/bin/env python3
"""Test script for the DuckDuckGo fallback functionality."""

import os
import sys
import json
import tempfile
import logging
from pathlib import Path

# Set up minimal environment variables for testing
os.environ["LOG_DIR"] = tempfile.gettempdir()
os.environ["WEBCAT_API_KEY"] = "test_key_for_testing"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_duckduckgo_fallback():
    """Test the DuckDuckGo fallback when no Serper API key is set."""
    print("🔍 Testing DuckDuckGo fallback functionality...")
    
    # Temporarily clear any existing API key
    original_serper_key = os.environ.get("SERPER_API_KEY", "")
    os.environ["SERPER_API_KEY"] = ""
    
    try:
        # Import the modules from current directory
        import sys
        from pathlib import Path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        from mcp_server import fetch_duckduckgo_search_results
        
        # Test DuckDuckGo search directly
        print("📡 Testing DuckDuckGo search with query: 'What is the capital of France?'")
        
        results = fetch_duckduckgo_search_results("What is the capital of France?", max_results=2)
        
        assert results is not None, "DuckDuckGo search should return results"
        assert len(results) > 0, "DuckDuckGo should return at least one result"
        
        print(f"✅ Success! DuckDuckGo returned {len(results)} results")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result.get('title', 'No title')}")
            print(f"  URL: {result.get('link', 'No URL')}")
            print(f"  Snippet: {result.get('snippet', 'No snippet')[:100]}...")
            
            # Verify result structure
            assert 'title' in result, f"Result {i} should have a title"
            assert 'link' in result, f"Result {i} should have a link"
            assert 'snippet' in result, f"Result {i} should have a snippet"
        
        print("\n✅ DuckDuckGo fallback test passed!")
        
    except ImportError as e:
        import pytest
        pytest.fail(f"Import error: {str(e)}")
    except Exception as e:
        import pytest
        pytest.fail(f"Test failed with error: {str(e)}")
    finally:
        # Restore original API key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key
        else:
            os.environ.pop("SERPER_API_KEY", None)

if __name__ == "__main__":
    # For direct execution (not pytest)
    import pytest
    test_duckduckgo_fallback()
    print("\n🎉 All tests passed! DuckDuckGo fallback is working correctly.") 