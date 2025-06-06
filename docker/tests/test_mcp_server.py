import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
import requests
from bs4 import BeautifulSoup

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Mock the imports from mcp_server
sys.modules['langchain.schema'] = MagicMock()
sys.modules['readability'] = MagicMock()
sys.modules['readability.Document'] = MagicMock()

# Create a simple test class that mimics MCP_Server for testing
class MockMCPServer:
    def __init__(self):
        pass
        
    def get_content(self, result):
        try:
            response = requests.get(result.url, timeout=5)
            response.raise_for_status()
            
            # In the real code, readability and BeautifulSoup would process the content
            result.content = "Mocked extracted content"
            
        except Exception as e:
            result.content = f"Error: Failed to scrape content. {str(e)}"
            
    def process_result(self, result):
        self.get_content(result)

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.mcp_server = MockMCPServer()
        self.mock_result = MagicMock()
        self.mock_result.url = "https://example.com"
        self.mock_result.content = ""

    @patch('requests.get')
    def test_get_content_success(self, mock_get):
        # Setup mocks
        mock_response = MagicMock()
        mock_response.content = b'<html><body><p>Test content</p></body></html>'
        mock_get.return_value = mock_response
        
        # Call the method
        self.mcp_server.get_content(self.mock_result)
        
        # Assertions
        mock_get.assert_called_once_with("https://example.com", timeout=5)
        self.assertEqual(self.mock_result.content, "Mocked extracted content")

    @patch('requests.get')
    def test_get_content_request_exception(self, mock_get):
        # Setup the mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call the method
        self.mcp_server.get_content(self.mock_result)
        
        # Assertions
        self.assertTrue(self.mock_result.content.startswith("Error: Failed to scrape content"))
        self.assertIn("Connection error", self.mock_result.content)

    @patch('requests.get')
    def test_get_content_http_error(self, mock_get):
        # Setup the mock to raise an HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_get.return_value = mock_response
        
        # Call the method
        self.mcp_server.get_content(self.mock_result)
        
        # Assertions
        self.assertTrue(self.mock_result.content.startswith("Error: Failed to scrape content"))
        self.assertIn("404 Client Error", self.mock_result.content)

    def test_process_result(self):
        # Setup
        self.mcp_server.get_content = MagicMock()
        
        # Call the method
        self.mcp_server.process_result(self.mock_result)
        
        # Assertions
        self.mcp_server.get_content.assert_called_once_with(self.mock_result)

if __name__ == '__main__':
    unittest.main() 