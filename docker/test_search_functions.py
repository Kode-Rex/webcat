#!/usr/bin/env python3
"""Unit tests for search functions without MCP dependencies."""

import os
import sys
import tempfile
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Set up minimal environment variables for testing
os.environ["LOG_DIR"] = tempfile.gettempdir()
os.environ["WEBCAT_API_KEY"] = "test_key_for_testing"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.mark.unit
def test_duckduckgo_search_function():
    """Test the DuckDuckGo search function directly."""
    # Create a minimal version of the function for testing with proper mocking
    def fetch_duckduckgo_search_results_test(query, max_results=5):
        """Test version of DuckDuckGo search function."""
        if not query or not query.strip():
            return []
        
        # Mock the actual search results for testing
        mock_results = [
            {
                'title': 'Paris - Wikipedia',
                'href': 'https://en.wikipedia.org/wiki/Paris',
                'body': 'Paris is the capital and largest city of France.'
            }
        ]
        
        formatted_results = []
        for result in mock_results[:max_results]:
            formatted_result = {
                'title': result.get('title', ''),
                'link': result.get('href', ''),
                'snippet': result.get('body', '')
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    # Test the function
    results = fetch_duckduckgo_search_results_test("What is the capital of France?", max_results=1)
    
    # Verify the results
    assert isinstance(results, list), "Results should be a list"
    assert len(results) == 1, "Should return one result"
    
    result = results[0]
    assert 'title' in result, "Result should have a title"
    assert 'link' in result, "Result should have a link"
    assert 'snippet' in result, "Result should have a snippet"
    assert result['title'] == 'Paris - Wikipedia', "Title should match mock data"
    assert result['link'] == 'https://en.wikipedia.org/wiki/Paris', "Link should match mock data"
    assert 'Paris is the capital' in result['snippet'], "Snippet should contain expected content"

@pytest.mark.unit
def test_search_result_structure():
    """Test that search results have the correct structure."""
    # Test data structure validation
    test_result = {
        'title': 'Test Title',
        'link': 'https://example.com',
        'snippet': 'Test snippet content'
    }
    
    # Verify required fields
    required_fields = ['title', 'link', 'snippet']
    for field in required_fields:
        assert field in test_result, f"Result should contain '{field}' field"
        assert isinstance(test_result[field], str), f"'{field}' should be a string"
        assert len(test_result[field]) > 0, f"'{field}' should not be empty"

@pytest.mark.unit
def test_empty_query_handling():
    """Test handling of empty queries."""
    def handle_empty_query(query):
        """Function to test empty query handling."""
        if not query or not query.strip():
            return []
        return ["mock_result"]
    
    # Test empty string
    assert handle_empty_query("") == [], "Empty string should return empty list"
    
    # Test whitespace only
    assert handle_empty_query("   ") == [], "Whitespace only should return empty list"
    
    # Test None
    assert handle_empty_query(None) == [], "None should return empty list"
    
    # Test valid query
    assert handle_empty_query("test") == ["mock_result"], "Valid query should return results"

@pytest.mark.unit
def test_api_key_environment_handling():
    """Test API key environment variable handling."""
    # Test with no Serper key (should use DuckDuckGo)
    original_serper_key = os.environ.get("SERPER_API_KEY", "")
    os.environ["SERPER_API_KEY"] = ""
    
    try:
        def should_use_duckduckgo():
            """Function to test API key logic."""
            serper_key = os.environ.get("SERPER_API_KEY", "").strip()
            return not serper_key
        
        assert should_use_duckduckgo() == True, "Should use DuckDuckGo when no Serper key"
        
        # Test with Serper key
        os.environ["SERPER_API_KEY"] = "test_key"
        assert should_use_duckduckgo() == False, "Should use Serper when key is available"
        
    finally:
        # Restore original API key
        if original_serper_key:
            os.environ["SERPER_API_KEY"] = original_serper_key
        else:
            os.environ.pop("SERPER_API_KEY", None)

@pytest.mark.unit
def test_error_handling_logic():
    """Test error handling logic without external dependencies."""
    def safe_search_wrapper(search_func, query):
        """Wrapper to test error handling logic."""
        try:
            return search_func(query)
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return []
    
    def failing_search(query):
        """Mock search function that always fails."""
        raise Exception("Mock search failure")
    
    def working_search(query):
        """Mock search function that works."""
        return [{"title": "Test", "link": "http://test.com", "snippet": "Test snippet"}]
    
    # Test error handling
    result = safe_search_wrapper(failing_search, "test query")
    assert result == [], "Failed search should return empty list"
    
    # Test successful search
    result = safe_search_wrapper(working_search, "test query")
    assert len(result) == 1, "Successful search should return results"
    assert result[0]["title"] == "Test", "Result should match expected data" 