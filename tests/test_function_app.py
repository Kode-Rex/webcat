import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock, mock_open

# Add the src directory to the path so we can import the function_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import function_app

@pytest.fixture
def mock_http_request():
    """Create a mock HTTP request object with a JSON body."""
    class MockHttpRequest:
        def __init__(self, body=None):
            self.body = body
            
        def get_json(self):
            return json.loads(self.body) if self.body else None
    
    return MockHttpRequest

def test_set_api_key(mock_http_request):
    """Test setting the API key."""
    # Create a mock request with an API key
    request = mock_http_request(body='{"api_key": "test_api_key"}')
    
    # Reset the global API key
    function_app.SERPER_API_KEY = ""
    
    # Call the function
    response = function_app.set_api_key(request)
    
    # Check the response
    assert response.status_code == 200
    assert response.get_body().decode() == "API key set successfully"
    assert function_app.SERPER_API_KEY == "test_api_key"

def test_set_api_key_missing(mock_http_request):
    """Test setting an empty API key."""
    # Create a mock request with no API key
    request = mock_http_request(body='{}')
    
    # Call the function
    response = function_app.set_api_key(request)
    
    # Check the response
    assert response.status_code == 400
    assert "Error: Missing API key" in response.get_body().decode()

@patch('function_app.requests.get')
def test_fetch_content(mock_get, mock_http_request):
    """Test the fetch_content function."""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.content = b'<html><body><article><p>Test content</p></article></body></html>'
    mock_response.encoding = 'utf-8'
    mock_get.return_value = mock_response
    
    # Call the function
    soup = function_app.fetch_content('https://example.com', {'User-Agent': 'test'})
    
    # Check the result
    assert 'Test content' in soup.get_text()
    mock_get.assert_called_once_with('https://example.com', headers={'User-Agent': 'test'})

@patch('function_app.try_fetch_with_backoff')
def test_scrape(mock_fetch, mock_http_request):
    """Test the scrape function."""
    # Set up the mock
    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "Test content"
    mock_fetch.return_value = mock_soup
    
    # Create a mock request
    request = mock_http_request(body='{"url": "https://example.com"}')
    
    # Call the function
    response = function_app.scrape(request)
    
    # Check the response
    assert response.status_code == 200
    assert "Test content" in response.get_body().decode()
    mock_fetch.assert_called_once()

@patch('function_app.try_fetch_with_backoff')
def test_scrape_missing_url(mock_fetch, mock_http_request):
    """Test the scrape function with missing URL."""
    # Create a mock request with no URL
    request = mock_http_request(body='{}')
    
    # Call the function
    response = function_app.scrape(request)
    
    # Check the response
    assert response.status_code == 400
    assert "Error: Missing URL" in response.get_body().decode()
    mock_fetch.assert_not_called()

@patch('function_app.requests.post')
@patch('function_app.try_fetch_with_backoff')
def test_search(mock_fetch, mock_post, mock_http_request):
    """Test the search function."""
    # Set up the mocks
    function_app.SERPER_API_KEY = "test_api_key"
    
    # Mock the Serper API response
    mock_serper_response = MagicMock()
    mock_serper_response.json.return_value = {
        'organic': [
            {'title': 'Test Result 1', 'link': 'https://example.com/1', 'snippet': 'Test snippet 1'},
            {'title': 'Test Result 2', 'link': 'https://example.com/2', 'snippet': 'Test snippet 2'},
        ]
    }
    mock_post.return_value = mock_serper_response
    
    # Mock the content fetching
    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "Test content"
    mock_fetch.return_value = mock_soup
    
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
    assert "Test content" in response_body["results"][0]["content"]
    
    # Verify that the Serper API was called correctly
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["headers"]["X-API-KEY"] == "test_api_key"
    assert mock_post.call_args[1]["json"]["q"] == "test query"

@patch('function_app.try_fetch_with_backoff')
def test_scrape_with_images(mock_fetch, mock_http_request):
    """Test the scrape_with_images function."""
    # Set up the mock BeautifulSoup object
    mock_soup = MagicMock()
    
    # Create text nodes and img elements to simulate traversing the soup
    text_node1 = "This is text part 1"
    text_node2 = "This is text part 2"
    
    # Create mock img tags with src attributes
    img1 = MagicMock()
    img1.name = 'img'
    img1.get.return_value = 'https://example.com/image1.jpg'
    
    img2 = MagicMock()
    img2.name = 'img'
    img2.get.return_value = 'https://example.com/image2.jpg'
    
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