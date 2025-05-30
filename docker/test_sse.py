#!/usr/bin/env python3
"""Test script for the SSE endpoint."""

import requests
import json
import sseclient
import os
import argparse
import socket

def check_container_ports():
    """Check which containers and ports are running."""
    print("Checking available WebCAT services:")
    
    # Check port 9000 (our new container)
    try:
        response = requests.get("http://localhost:9000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Port 9000 (new webcat-test container): AVAILABLE")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Port 9000: UNAVAILABLE (Status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Port 9000: UNAVAILABLE - {str(e)}")

def test_sse(webcat_api_key=None):
    """Test the SSE endpoint.
    
    Args:
        webcat_api_key: The WebCAT API key to use for authentication.
                        This key is used to authenticate with the WebCAT API.
    """
    # First check which servers are available
    check_container_ports()
    
    # Get WebCAT API key from parameter or environment
    if not webcat_api_key:
        webcat_api_key = os.environ.get("WEBCAT_API_KEY", "")
        
    if not webcat_api_key:
        print("Error: No WebCAT API key provided. Please provide a key with --api-key or set WEBCAT_API_KEY environment variable")
        return
    
    # Use the endpoint format expected by the server
    # The API key in the URL is used for authentication with WebCAT API
    url = f"http://localhost:9000/search/{webcat_api_key}/sse"
    
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "query": "What is the capital of France?"
    }
    
    print(f"Testing SSE endpoint: {url}")
    print(f"Using WebCAT API key: {webcat_api_key[:4]}...{webcat_api_key[-4:] if len(webcat_api_key) > 8 else '****'}")
    
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return
        
        client = sseclient.SSEClient(response)
        
        print("Streaming response from SSE endpoint:")
        for event in client.events():
            print(f"Event: {event.event}")
            print(f"Data: {event.data}")
            print("---")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test SSE endpoint')
    parser.add_argument('--api-key', 
                        help="WebCAT API key for authentication")
    args = parser.parse_args()
    
    test_sse(webcat_api_key=args.api_key) 