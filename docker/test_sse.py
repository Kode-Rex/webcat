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
        
    # Check port 8765 (old insight-mesh container)
    try:
        response = requests.get("http://localhost:8765/health", timeout=2)
        if response.status_code == 200:
            print("✅ Port 8765 (old insight-mesh-webcat container): AVAILABLE")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Port 8765: UNAVAILABLE (Status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Port 8765: UNAVAILABLE - {str(e)}")
    
    print("---")

def test_sse(use_server_key=False):
    """Test the SSE endpoint.
    
    Args:
        use_server_key: If True, use the server's WEBCAT_API_KEY by specifying 'webcat'
                        as the API key in the URL path.
    """
    # First check which servers are available
    check_container_ports()
    
    if use_server_key:
        # Use 'webcat' as the API key to use the server's WEBCAT_API_KEY
        api_key = "webcat"
        print("Using server's WEBCAT_API_KEY for authentication")
    else:
        # Get API key from environment
        api_key = os.environ.get("SERPER_API_KEY", "")
        if not api_key:
            print("Warning: No API key provided. Set SERPER_API_KEY environment variable or use --server-key")
            print("API requests will likely fail without a valid API key")
    
    # Use the simplified endpoint format on port 9000 (new container)
    url = f"http://localhost:9000/search/{api_key}/sse"
    
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "query": "What is the capital of France?"
    }
    
    print(f"Testing SSE endpoint: {url}")
    
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
    parser.add_argument('--server-key', action='store_true', 
                        help="Use server's WEBCAT_API_KEY instead of your own SERPER_API_KEY")
    args = parser.parse_args()
    
    test_sse(use_server_key=args.server_key) 