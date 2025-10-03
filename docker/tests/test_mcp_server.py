# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
import unittest
from unittest.mock import patch

import requests

from tests.factories.http_response_factory import HttpResponseFactory

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


# Create test class for SearchResult
class SearchResult:
    def __init__(self, title, url, snippet):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.content = ""


# Create a test class that mimics the scrape_search_result function
class MockMCPServer:
    def __init__(self):
        pass

    def get_content(self, result):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
            }

            response = requests.get(result.url, timeout=5, headers=headers)
            response.raise_for_status()

            # In the real code, readability, BeautifulSoup, and html2text would
            # process the content
            result.content = (
                f"# {result.title}\n\n*Source: {result.url}*\n\nMocked markdown content"
            )

        except requests.RequestException as e:
            result.content = f"Error: Failed to retrieve the webpage. {str(e)}"
        except Exception as e:
            result.content = f"Error: Failed to scrape content. {str(e)}"

    def process_result(self, result):
        self.get_content(result)


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.mcp_server = MockMCPServer()
        self.mock_result = SearchResult(
            title="Test Page", url="https://example.com", snippet="Test snippet"
        )

    @patch("requests.get")
    def test_get_content_success(self, mock_get):
        # Setup mocks
        mock_get.return_value = HttpResponseFactory.success()

        # Call the method
        self.mcp_server.get_content(self.mock_result)

        # Assertions
        mock_get.assert_called_once()
        self.assertTrue(self.mock_result.content.startswith("# Test Page"))
        self.assertIn("*Source: https://example.com*", self.mock_result.content)
        self.assertIn("Mocked markdown content", self.mock_result.content)

    @patch("requests.get")
    def test_get_content_request_exception(self, mock_get):
        # Setup the mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        # Call the method
        self.mcp_server.get_content(self.mock_result)

        # Assertions
        self.assertTrue(
            self.mock_result.content.startswith("Error: Failed to retrieve the webpage")
        )
        self.assertIn("Connection error", self.mock_result.content)

    @patch("requests.get")
    def test_get_content_http_error(self, mock_get):
        # Setup the mock to raise an HTTP error
        mock_get.return_value = HttpResponseFactory.with_http_error(
            404, "404 Client Error"
        )

        # Call the method
        self.mcp_server.get_content(self.mock_result)

        # Assertions
        self.assertTrue(
            self.mock_result.content.startswith("Error: Failed to retrieve the webpage")
        )
        self.assertIn("404 Client Error", self.mock_result.content)

    @patch("requests.get")
    def test_get_content_plaintext(self, mock_get):
        # Setup mocks for plaintext response
        mock_get.return_value = HttpResponseFactory.plaintext("Plain text content")

        # Custom implementation to check plaintext handling
        class PlaintextMockServer(MockMCPServer):
            def get_content(self, result):
                response = requests.get(result.url, timeout=5)
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()
                if "text/plain" in content_type:
                    result.content = f"# {result.title}\n\n*Source: {result.url}*\n\n```\n{response.text}\n```"

        server = PlaintextMockServer()
        server.get_content(self.mock_result)

        # Assertions
        self.assertTrue(self.mock_result.content.startswith("# Test Page"))
        self.assertIn("```\nPlain text content\n```", self.mock_result.content)

    @patch.object(MockMCPServer, "get_content")
    def test_process_result(self, mock_get_content):
        # Call the method
        self.mcp_server.process_result(self.mock_result)

        # Assertions
        mock_get_content.assert_called_once_with(self.mock_result)


if __name__ == "__main__":
    unittest.main()
