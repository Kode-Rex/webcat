#!/usr/bin/env python3
"""Test script for the DuckDuckGo fallback functionality."""

import os
import sys
import tempfile
import logging
import pytest
from pathlib import Path

# Set up minimal environment variables for testing
os.environ["LOG_DIR"] = tempfile.gettempdir()
# No API key needed for testing

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.mark.integration
def test_duckduckgo_fallback():
    """Test the DuckDuckGo fallback when no Serper API key is set."""
    print("🔍 Testing DuckDuckGo fallback functionality...")
    
    # Temporarily clear any existing API key
    original_serper_key = os.environ.get("SERPER_API_KEY", "")
    os.environ["SERPER_API_KEY"] = ""
    
    try:
        # Import the modules from current directory
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
        pytest.skip(f"Import error (requires full MCP server): {str(e)}")
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")
    finally:
        # Restore original API key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key
        else:
            os.environ.pop("SERPER_API_KEY", None)

@pytest.mark.integration
def test_duckduckgo_search_structure():
    """Test that DuckDuckGo search returns properly structured results."""
    # Clear API key to force DuckDuckGo usage
    original_serper_key = os.environ.get("SERPER_API_KEY", "")
    os.environ["SERPER_API_KEY"] = ""
    
    try:
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        from mcp_server import fetch_duckduckgo_search_results
        
        results = fetch_duckduckgo_search_results("Python programming", max_results=1)
        
        assert isinstance(results, list), "Results should be a list"
        if results:  # If we got results
            result = results[0]
            assert isinstance(result, dict), "Each result should be a dictionary"
            
            # Check required fields
            required_fields = ['title', 'link', 'snippet']
            for field in required_fields:
                assert field in result, f"Result should contain '{field}' field"
                assert isinstance(result[field], str), f"'{field}' should be a string"
                assert len(result[field]) > 0, f"'{field}' should not be empty"
    
    except ImportError as e:
        pytest.skip(f"Import error (requires full MCP server): {str(e)}")
    finally:
        # Restore original API key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key
        else:
            os.environ.pop("SERPER_API_KEY", None)

@pytest.mark.integration
def test_duckduckgo_error_handling():
    """Test that DuckDuckGo search handles errors gracefully."""
    # Clear API key to force DuckDuckGo usage
    original_serper_key = os.environ.get("SERPER_API_KEY", "")
    os.environ["SERPER_API_KEY"] = ""
    
    try:
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        from mcp_server import fetch_duckduckgo_search_results
        
        # Test with empty query
        results = fetch_duckduckgo_search_results("", max_results=1)
        assert isinstance(results, list), "Should return empty list for empty query"
        
        # Test with very long query (should not crash)
        long_query = "a" * 1000
        results = fetch_duckduckgo_search_results(long_query, max_results=1)
        assert isinstance(results, list), "Should handle long queries gracefully"
    
    except ImportError as e:
        pytest.skip(f"Import error (requires full MCP server): {str(e)}")
    finally:
        # Restore original API key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key
        else:
            os.environ.pop("SERPER_API_KEY", None) 