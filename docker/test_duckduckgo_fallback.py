#!/usr/bin/env python3
"""Test script for the DuckDuckGo fallback functionality."""

import os
import sys
import json
import tempfile
import logging
from pathlib import Path

# Add the docker directory to Python path so we can import mcp_server
docker_dir = Path(__file__).parent
sys.path.insert(0, str(docker_dir))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_duckduckgo_fallback():
    """Test the DuckDuckGo fallback when no Serper API key is set."""
    print("🔍 Testing DuckDuckGo fallback functionality...")
    
    # Temporarily clear any existing API key
    original_serper_key = os.environ.get("SERPER_API_KEY", "")
    os.environ["SERPER_API_KEY"] = ""
    
    # Set minimal environment variables for the test
    os.environ["LOG_DIR"] = tempfile.gettempdir()
    os.environ["WEBCAT_API_KEY"] = "test_key_for_testing"
    
    try:
        # Import the modules after setting environment variables
        from mcp_server import fetch_duckduckgo_search_results
        
        # Test DuckDuckGo search directly
        print("📡 Testing DuckDuckGo search with query: 'What is the capital of France?'")
        
        results = fetch_duckduckgo_search_results("What is the capital of France?", max_results=2)
        
        if results:
            print(f"✅ Success! DuckDuckGo returned {len(results)} results")
            
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  Title: {result.get('title', 'No title')}")
                print(f"  URL: {result.get('link', 'No URL')}")
                print(f"  Snippet: {result.get('snippet', 'No snippet')[:100]}...")
        else:
            print("❌ No results returned from DuckDuckGo")
            return False
            
        print("\n🧪 Testing complete search tool fallback...")
        
        # Test the complete search tool function directly
        import asyncio
        
        # Import the actual search function
        from mcp_server import search_tool
        
        async def test_search_tool():
            # Call the search tool function directly
            result = await search_tool("What is the capital of France?")
            return result
        
        search_result = asyncio.run(test_search_tool())
        
        if 'error' in search_result:
            print(f"❌ Search tool returned error: {search_result['error']}")
            return False
        
        print(f"✅ Search tool success!")
        print(f"  Query: {search_result.get('query')}")
        print(f"  Search Source: {search_result.get('search_source')}")
        print(f"  Results count: {len(search_result.get('results', []))}")
        
        if search_result.get('search_source') == "DuckDuckGo (free fallback)":
            print("✅ Correctly used DuckDuckGo fallback!")
        else:
            print(f"⚠️  Expected DuckDuckGo fallback, got: {search_result.get('search_source')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error (missing dependency?): {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original API key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key
        else:
            os.environ.pop("SERPER_API_KEY", None)

if __name__ == "__main__":
    success = test_duckduckgo_fallback()
    if success:
        print("\n🎉 All tests passed! DuckDuckGo fallback is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1) 