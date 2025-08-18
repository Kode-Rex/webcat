# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

import function_app

# Update the import path to use the current directory structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock html2text module
sys.modules["html2text"] = MagicMock()
sys.modules["html2text"].HTML2Text = MagicMock()


@pytest.fixture
def mock_http_request():
    """Create a mock HTTP request object with a JSON body."""

    class MockHttpRequest:
        def __init__(self, body=None):
            self.body = body

        def get_json(self):
            return json.loads(self.body) if self.body else None

    return MockHttpRequest


@patch("function_app.requests.get")
@patch("function_app.Document")
def test_fetch_content(mock_document, mock_get, mock_http_request):
    """Test the fetch_content function."""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.content = b"<html><head><title>Test Page</title></head><body><article><p>Test content</p></article></body></html>"
    mock_response.encoding = "utf-8"
    mock_get.return_value = mock_response

    # Setup mock Document instance
    mock_doc = MagicMock()
    mock_doc.title.return_value = "Test Page"
    mock_doc.summary.return_value = "<p>Test content</p>"
    mock_document.return_value = mock_doc

    # Mock html2text
    MagicMock()
    mock_h = MagicMock()
    mock_h.handle.return_value = "Test content in markdown"
    function_app.html2text.HTML2Text = MagicMock(return_value=mock_h)

    # Call the function
    soup = function_app.fetch_content("https://example.com", {"User-Agent": "test"})

    # Check the result
    assert hasattr(soup, "markdown_content")
    assert "Test Page" in soup.markdown_content
    assert "Source: https://example.com" in soup.markdown_content
    assert "Test content in markdown" in soup.markdown_content
    mock_get.assert_called_once_with(
        "https://example.com", headers={"User-Agent": "test"}
    )


@patch("function_app.try_fetch_with_backoff")
def test_scrape(mock_fetch, mock_http_request):
    """Test the scrape function."""
    # Set up the mock
    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "Test content"
    mock_soup.markdown_content = (
        "# Test Page\n\n*Source: https://example.com*\n\nTest content in markdown"
    )
    mock_fetch.return_value = mock_soup

    # Create a mock request
    request = mock_http_request(body='{"url": "https://example.com"}')

    # Call the function
    response = function_app.scrape(request)

    # Check the response
    assert response.status_code == 200
    content = response.get_body().decode()
    assert "Test Page" in content
    assert "Source: https://example.com" in content
    assert "Test content in markdown" in content
    mock_fetch.assert_called_once()


@patch("function_app.try_fetch_with_backoff")
def test_scrape_missing_url(mock_fetch, mock_http_request):
    """Test the scrape function with missing URL."""
    # Create a mock request with no URL
    request = mock_http_request(body="{}")

    # Call the function
    response = function_app.scrape(request)

    # Check the response
    assert response.status_code == 400
    assert "Error: Missing URL" in response.get_body().decode()
    mock_fetch.assert_not_called()


@patch("function_app.requests.post")
@patch("function_app.try_fetch_with_backoff")
def test_search(mock_fetch, mock_post, mock_http_request):
    """Test the search function."""
    # Set up the mocks
    function_app.SERPER_API_KEY = "test_api_key"  # pragma: allowlist secret

    # Mock the Serper API response
    mock_serper_response = MagicMock()
    mock_serper_response.json.return_value = {
        "organic": [
            {
                "title": "Test Result 1",
                "link": "https://example.com/1",
                "snippet": "Test snippet 1",
            },
            {
                "title": "Test Result 2",
                "link": "https://example.com/2",
                "snippet": "Test snippet 2",
            },
        ]
    }
    mock_post.return_value = mock_serper_response

    # Mock the content fetching
    mock_soup1 = MagicMock()
    mock_soup1.get_text.return_value = "Test content 1"
    mock_soup1.markdown_content = (
        "# Test Result 1\n\n*Source: https://example.com/1*\n\nMarkdown content 1"
    )

    mock_soup2 = MagicMock()
    mock_soup2.get_text.return_value = "Test content 2"
    mock_soup2.markdown_content = (
        "# Test Result 2\n\n*Source: https://example.com/2*\n\nMarkdown content 2"
    )

    mock_fetch.side_effect = [mock_soup1, mock_soup2]

    # Create a mock request
    request = mock_http_request(body='{"query": "test query"}')

    # Call the function
    response = function_app.search(request)

    # Check the response
    assert response.status_code == 200
    response_body = json.loads(response.get_body().decode())
    assert response_body["query"] == "test query"
    assert response_body["result_count"] == 2
    assert len(response_body["results"]) == 2
    assert response_body["results"][0]["title"] == "Test Result 1"
    assert response_body["results"][0]["url"] == "https://example.com/1"
    assert "Markdown content 1" in response_body["results"][0]["content"]

    # Verify that the Serper API was called correctly
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["headers"]["X-API-KEY"] == "test_api_key"
    assert mock_post.call_args[1]["json"]["q"] == "test query"


@patch("function_app.try_fetch_with_backoff")
def test_scrape_with_images(mock_fetch, mock_http_request):
    """Test the scrape_with_images function."""
    # Set up the mock BeautifulSoup object
    mock_soup = MagicMock()

    # Create text nodes and img elements to simulate traversing the soup
    text_node1 = "This is text part 1"
    text_node2 = "This is text part 2"

    # Create mock img tags with src attributes
    img1 = MagicMock()
    img1.name = "img"
    img1.get.return_value = "https://example.com/image1.jpg"

    img2 = MagicMock()
    img2.name = "img"
    img2.get.return_value = "https://example.com/image2.jpg"

    # Set up the descendants to be iterated over
    mock_soup.descendants = [text_node1, img1, text_node2, img2]
    mock_fetch.return_value = mock_soup

    # Create a mock request
    request = mock_http_request(body='{"url": "https://example.com"}')

    # Call the function
    response = function_app.scrape_with_images(request)

    # Check the response
    assert response.status_code == 200
    response_body = json.loads(response.get_body().decode())

    # Check that the text and images are in the response
    assert "This is text part 1" in response_body["content"]
    assert "This is text part 2" in response_body["content"]
    assert "https://example.com/image1.jpg" in response_body["content"]
    assert "https://example.com/image2.jpg" in response_body["content"]

    # Verify that the fetch function was called
    mock_fetch.assert_called_once()
