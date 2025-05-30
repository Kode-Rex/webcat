import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient

# Add the parent directory to the path to import mcp package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from mcp package
from mcp.app import app
from mcp.services import scrape_search_result
from mcp.models import SearchResult

# Initialize test client
client = TestClient(app)

class TestMCPServer(unittest.TestCase):
    """Tests for the MCP server."""
    
    @patch('mcp.app.fetch_search_results')
    def test_search_no_results(self, mock_fetch):
        """Test search with no results."""
        # Mock the fetch_search_results function to return empty results
        mock_fetch.return_value = []
        
        # Make the request with an API key to bypass validation
        response = client.post(
            "/api/search",
            json={"query": "test query", "api_key": "test_api_key"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 404)
        self.assertIn("No search results found", response.text)
        mock_fetch.assert_called_once()
    
    @patch('mcp.app.fetch_search_results')
    @patch('mcp.app.process_search_results')
    def test_search_with_results(self, mock_process, mock_fetch):
        """Test search with results."""
        # Mock the fetch_search_results function
        mock_fetch.return_value = [
            {'title': 'Result 1', 'link': 'https://example.com/1', 'snippet': 'Snippet 1'},
            {'title': 'Result 2', 'link': 'https://example.com/2', 'snippet': 'Snippet 2'},
            {'title': 'Result 3', 'link': 'https://example.com/3', 'snippet': 'Snippet 3'},
        ]
        
        # Mock the process_search_results function
        mock_process.return_value = [
            SearchResult(
                title='Result 1',
                url='https://example.com/1',
                snippet='Snippet 1',
                content='Content for Result 1'
            ),
            SearchResult(
                title='Result 2',
                url='https://example.com/2',
                snippet='Snippet 2',
                content='Content for Result 2'
            ),
            SearchResult(
                title='Result 3',
                url='https://example.com/3',
                snippet='Snippet 3',
                content='Content for Result 3'
            ),
        ]
        
        # Make the request with an API key to bypass validation
        response = client.post(
            "/api/search",
            json={"query": "test query", "api_key": "test_api_key"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["query"], "test query")
        self.assertEqual(data["result_count"], 3)
        self.assertEqual(len(data["results"]), 3)
        
        # Due to parallel processing, results might come back in any order
        # Check that all expected results are in the response, regardless of order
        titles = [result["title"] for result in data["results"]]
        self.assertIn("Result 1", titles)
        self.assertIn("Result 2", titles)
        self.assertIn("Result 3", titles)
        
        # Check content format for all results
        for result in data["results"]:
            self.assertIn(f"Content for {result['title']}", result["content"])
        
        # Verify mocks were called
        mock_fetch.assert_called_once()
        mock_process.assert_called_once()
    
    def test_search_missing_api_key(self):
        """Test search with missing API key."""
        # No need to patch the fetch function here as we're testing the API key validation
        
        # Make the request without an API key
        response = client.post(
            "/api/search",
            json={"query": "test query"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Serper API key not configured", response.text)
        
        # Now with a properly mocked fetch_search_results
        with patch('mcp.app.fetch_search_results') as mock_fetch:
            # Return empty results for the 404
            mock_fetch.return_value = []
            
            # Make the request with an API key in the request
            response = client.post(
                "/api/search",
                json={"query": "test query", "api_key": "request_api_key"}
            )
            
            # This should now succeed and call the fetch_search_results function
            self.assertEqual(response.status_code, 404)  # Will be 404 as we mock empty results
            mock_fetch.assert_called_once()
    
    @patch('mcp.utils.requests.get')
    def test_scrape_search_result(self, mock_get):
        """Test the scrape_search_result function."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.content = b'<html><body><article><p>Test content</p></article></body></html>'
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        # Test result with URL
        result = {
            'title': 'Test Result',
            'link': 'https://example.com',
            'snippet': 'Test snippet',
        }
        
        search_result = scrape_search_result(result)
        
        # Check the result
        self.assertEqual(search_result.title, 'Test Result')
        self.assertEqual(search_result.url, 'https://example.com')
        self.assertEqual(search_result.snippet, 'Test snippet')
        self.assertIn('Test content', search_result.content)
        
        # Test result without URL
        result_no_url = {
            'title': 'Test Result No URL',
            'snippet': 'Test snippet no URL',
        }
        
        search_result_no_url = scrape_search_result(result_no_url)
        
        # Check the result
        self.assertEqual(search_result_no_url.title, 'Test Result No URL')
        self.assertEqual(search_result_no_url.url, '')
        self.assertEqual(search_result_no_url.snippet, 'Test snippet no URL')
        self.assertIn('Error: Missing URL', search_result_no_url.content)
    
    @patch('mcp.utils.requests.get')
    def test_scrape_search_result_error(self, mock_get):
        """Test the scrape_search_result function with an error."""
        # Make the get request raise an exception
        mock_get.side_effect = Exception("Test error")
        
        # Test result
        result = {
            'title': 'Test Result',
            'link': 'https://example.com',
            'snippet': 'Test snippet',
        }
        
        search_result = scrape_search_result(result)
        
        # Check the result
        self.assertEqual(search_result.title, 'Test Result')
        self.assertEqual(search_result.url, 'https://example.com')
        self.assertEqual(search_result.snippet, 'Test snippet')
        self.assertIn('Error: Failed to scrape content', search_result.content)
        self.assertIn('Test error', search_result.content)
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "mcp")

if __name__ == '__main__':
    unittest.main() 