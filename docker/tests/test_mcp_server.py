import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient
import tempfile

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set LOG_DIR to a temporary directory
os.environ["LOG_DIR"] = tempfile.gettempdir()

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
            "/search/test_api_key/rest",
            json={"query": "test query", "api_key": "test_api_key"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"], "No search results found")
    
    @patch('mcp.app.process_search_results')
    @patch('mcp.app.fetch_search_results')
    def test_search_with_results(self, mock_fetch, mock_process):
        """Test search with results."""
        # Mock the fetch_search_results function
        mock_fetch.return_value = [
            {'title': 'Result 1', 'link': 'https://example.com/1', 'snippet': 'Snippet 1'},
            {'title': 'Result 2', 'link': 'https://example.com/2', 'snippet': 'Snippet 2'},
            {'title': 'Result 3', 'link': 'https://example.com/3', 'snippet': 'Snippet 3'},
            {'title': 'Result 4', 'link': 'https://example.com/4', 'snippet': 'Snippet 4'},
            {'title': 'Result 5', 'link': 'https://example.com/5', 'snippet': 'Snippet 5'},
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
            SearchResult(
                title='Result 4',
                url='https://example.com/4',
                snippet='Snippet 4',
                content='Content for Result 4'
            ),
            SearchResult(
                title='Result 5',
                url='https://example.com/5',
                snippet='Snippet 5',
                content='Content for Result 5'
            ),
        ]
        
        # Make the request with an API key to bypass validation
        response = client.post(
            "/search/test_api_key/rest",
            json={"query": "test query", "api_key": "test_api_key"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["query"], "test query")
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["results"][0]["title"], "Result 1")
        self.assertEqual(data["results"][0]["url"], "https://example.com/1")
    
    def test_search_missing_api_key(self):
        """Test search with missing API key."""
        # No need to patch the fetch function here as we're testing the API key validation
        
        # Make the request without an API key in the URL path
        response = client.post(
            "/search//rest",
            json={"query": "test query"}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], "Authentication failed: No API key provided.")
    
    @patch('mcp.app.scrape_search_result')
    def test_scrape_search_result(self, mock_get):
        """Test the scrape_search_result function."""
        # Mock the get_page_content function
        mock_response = MagicMock()
        mock_response.content = b'<html><body><article><p>Test content</p></article></body></html>'
        mock_get.return_value = "Test content"
        
        # Test result with URL
        search_result = SearchResult(
            title='Test Result',
            url='https://example.com',
            snippet='Test snippet',
            content=''
        )
        
        search_result = scrape_search_result(search_result)
        
        self.assertEqual(search_result.title, 'Test Result')
        self.assertEqual(search_result.url, 'https://example.com')
        self.assertEqual(search_result.snippet, 'Test snippet')
        self.assertIn('Test content', search_result.content)
        
        # Test result without URL
        search_result_no_url = SearchResult(
            title='Test Result No URL',
            snippet='Test snippet no URL',
            content=''
        )
        
        search_result_no_url = scrape_search_result(search_result_no_url)
        
        self.assertEqual(search_result_no_url.title, 'Test Result No URL')
        self.assertEqual(search_result_no_url.url, '')
        self.assertEqual(search_result_no_url.snippet, 'Test snippet no URL')
    
    @patch('mcp.app.scrape_search_result')
    def test_scrape_search_result_error(self, mock_get):
        """Test the scrape_search_result function with an error."""
        # Mock the get_page_content function to raise an exception
        mock_get.side_effect = Exception("Test error")
        
        # Test result
        search_result = SearchResult(
            title='Test Result',
            url='https://example.com',
            snippet='Test snippet',
            content=''
        )
        
        search_result = scrape_search_result(search_result)
        
        self.assertEqual(search_result.title, 'Test Result')
        self.assertEqual(search_result.url, 'https://example.com')
        self.assertEqual(search_result.snippet, 'Test snippet')
        self.assertIn('Test error', search_result.content)
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "webcat")
    
    @patch('mcp.app.process_search_results')
    @patch('mcp.app.fetch_search_results')
    def test_rest_endpoint(self, mock_fetch, mock_process):
        """Test the RESTful endpoint."""
        # Mock the fetch_search_results function
        mock_fetch.return_value = [
            {'title': 'Result 1', 'link': 'https://example.com/1', 'snippet': 'Snippet 1'},
        ]
        
        # Mock the process_search_results function
        mock_process.return_value = [
            SearchResult(
                title='Result 1',
                url='https://example.com/1',
                snippet='Snippet 1',
                content='Content for Result 1'
            ),
        ]
        
        # Set environment variables for testing
        with patch('mcp.app.WEBCAT_API_KEY', 'test_webcat_key'):
            with patch('mcp.app.SERPER_API_KEY', 'test_serper_key'):
                # Make the request to the RESTful endpoint
                response = client.post(
                    "/search/test_webcat_key/rest",
                    json={"query": "test query"}
                )
                
                # Check the response
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["query"], "test query")
                self.assertEqual(len(data["results"]), 1)
                self.assertEqual(data["results"][0]["title"], "Result 1")
                
                # Test with invalid API key
                response = client.post(
                    "/search/invalid_key/rest",
                    json={"query": "test query"}
                )
                
                # Check the response
                self.assertEqual(response.status_code, 401)
                data = response.json()
                self.assertEqual(data["detail"], "Authentication failed: Invalid API key.")

if __name__ == '__main__':
    unittest.main() 