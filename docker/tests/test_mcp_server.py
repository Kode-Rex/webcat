import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the server
import mcp_server

# Initialize test client
client = TestClient(mcp_server.app)

class TestMCPServer(unittest.TestCase):
    """Tests for the MCP server."""
    
    def setUp(self):
        """Set up before each test."""
        # Set a test API key
        mcp_server.SERPER_API_KEY = "test_api_key"
    
    @patch('mcp_server.requests.post')
    def test_search_no_results(self, mock_post):
        """Test search with no results."""
        # Mock the Serper API response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {'organic': []}
        mock_post.return_value = mock_response
        
        # Make the request
        response = client.post(
            "/api/search",
            json={"query": "test query"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 404)
        self.assertIn("No search results found", response.text)
    
    @patch('mcp_server.requests.post')
    @patch('mcp_server.scrape_search_result')
    def test_search_with_results(self, mock_scrape, mock_post):
        """Test search with results."""
        # Mock the Serper API response with results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'organic': [
                {'title': 'Result 1', 'link': 'https://example.com/1', 'snippet': 'Snippet 1'},
                {'title': 'Result 2', 'link': 'https://example.com/2', 'snippet': 'Snippet 2'},
                {'title': 'Result 3', 'link': 'https://example.com/3', 'snippet': 'Snippet 3'},
            ]
        }
        mock_post.return_value = mock_response
        
        # Mock the scrape_search_result function
        def mock_scrape_side_effect(result):
            return mcp_server.SearchResult(
                title=result['title'],
                url=result['link'],
                snippet=result['snippet'],
                content=f"Content for {result['title']}"
            )
        
        mock_scrape.side_effect = mock_scrape_side_effect
        
        # Make the request
        response = client.post(
            "/api/search",
            json={"query": "test query"}
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
    
    @patch('mcp_server.requests.post')
    def test_search_missing_api_key(self, mock_post):
        """Test search with missing API key."""
        # Clear the API key
        mcp_server.SERPER_API_KEY = ""
        
        # Make the request without an API key
        response = client.post(
            "/api/search",
            json={"query": "test query"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Serper API key not configured", response.text)
        
        # Make the request with an API key in the request
        response = client.post(
            "/api/search",
            json={"query": "test query", "api_key": "request_api_key"}
        )
        
        # Check that the request would have proceeded (we'll just check that post was called)
        mock_post.assert_called_once()
    
    @patch('mcp_server.requests.get')
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
        
        search_result = mcp_server.scrape_search_result(result)
        
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
        
        search_result_no_url = mcp_server.scrape_search_result(result_no_url)
        
        # Check the result
        self.assertEqual(search_result_no_url.title, 'Test Result No URL')
        self.assertEqual(search_result_no_url.url, '')
        self.assertEqual(search_result_no_url.snippet, 'Test snippet no URL')
        self.assertIn('Error: Missing URL', search_result_no_url.content)
    
    @patch('mcp_server.requests.get')
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
        
        search_result = mcp_server.scrape_search_result(result)
        
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