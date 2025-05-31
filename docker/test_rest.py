"""Test script for the RESTful endpoint."""

import argparse
import json
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def test_rest(webcat_api_key=None):
    """Test the RESTful endpoint.
    
    Args:
        webcat_api_key: Optional API key to use. If not provided,
                        it will be read from the environment variable.
    
    Returns:
        bool: True if the test passed, False otherwise.
    """
    # Get API key from environment if not provided
    if not webcat_api_key:
        webcat_api_key = os.environ.get("WEBCAT_API_KEY")
        if not webcat_api_key:
            print("Error: No WebCAT API key provided or found in environment variables.")
            return False
    
    # Define the endpoint URL with the API key
    url = f"http://localhost:9000/search/{webcat_api_key}/rest"
    
    # Define the search query
    search_query = {
        "query": "Latest advancements in artificial intelligence"
    }
    
    # Make the HTTP request
    print(f"Testing RESTful endpoint: {url}")
    print(f"Search query: {search_query['query']}")
    
    try:
        response = requests.post(url, json=search_query)
        
        # Check the response status code
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Parse the JSON response
        data = response.json()
        
        # Print the response
        print("\nResponse from RESTful endpoint:")
        print(f"Query: {data['query']}")
        print(f"Result count: {data['result_count']}")
        
        # Print each result
        for i, result in enumerate(data['results'], 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Content snippet: {result['content'][:150]}...")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Test RESTful endpoint')
    parser.add_argument('--api-key', help='WebCAT API key to use for testing')
    args = parser.parse_args()
    
    # Run the test
    success = test_rest(webcat_api_key=args.api_key)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 