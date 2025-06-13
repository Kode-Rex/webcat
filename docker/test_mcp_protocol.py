#!/usr/bin/env python3
"""Test script for the MCP SSE protocol."""

import requests
import json
import os
import argparse
import time
import pytest

@pytest.mark.integration
def test_mcp_protocol():
    """Test the MCP SSE protocol.
    
    This is an integration test that requires a running MCP server.
    """
    # Check if server is running
    base_url = "http://localhost:8000/mcp/"
    
    print("🔍 Testing MCP Protocol with WebCat Server")
    print(f"📡 Endpoint: {base_url}")
    
    # Step 1: Initialize MCP session
    print("\n1️⃣ Initializing MCP session...")
    
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=init_payload)
        
        assert response.status_code == 200, f"Initialization failed: {response.status_code} - {response.text}"
        
        # Extract session ID from headers
        session_id = response.headers.get('mcp-session-id')
        assert session_id is not None, "No session ID returned in headers"
        
        print(f"✅ Session initialized! Session ID: {session_id}")
        
        # Step 2: Send initialized notification
        print("\n2️⃣ Sending initialized notification...")
        
        init_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        headers_with_session = headers.copy()
        headers_with_session["Mcp-Session-Id"] = session_id
        
        response = requests.post(base_url, headers=headers_with_session, json=init_notification)
        print("✅ Initialized notification sent")
        
        # Step 3: List available tools
        print("\n3️⃣ Listing available tools...")
        
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = requests.post(base_url, headers=headers_with_session, json=tools_payload)
        
        assert response.status_code == 200, f"Tools list failed: {response.status_code} - {response.text}"
        
        # Parse SSE response
        response_text = response.text
        tools_found = False
        if "event: message" in response_text:
            # Extract JSON from SSE format
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print(f"✅ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"   - {tool['name']}: {tool['description']}")
                        tools_found = True
                        assert len(tools) >= 2, "Should have at least 2 tools (search and health_check)"
                        break
        
        assert tools_found, "No tools found in response"
        
        # Step 4: Test search tool
        print("\n4️⃣ Testing search tool...")
        
        search_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": "What is the capital of France?"
                }
            }
        }
        
        response = requests.post(base_url, headers=headers_with_session, json=search_payload)
        
        assert response.status_code == 200, f"Search tool failed: {response.status_code} - {response.text}"
        
        # Parse search results
        response_text = response.text
        search_completed = False
        if "event: message" in response_text:
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if 'result' in data and 'content' in data['result']:
                        content = data['result']['content'][0]['text']
                        search_data = json.loads(content)
                        print(f"✅ Search completed!")
                        print(f"   Source: {search_data.get('search_source', 'Unknown')}")
                        print(f"   Results: {len(search_data.get('results', []))}")
                        if search_data.get('results'):
                            first_result = search_data['results'][0]
                            print(f"   First result: {first_result.get('title', 'No title')}")
                        
                        # Assertions for search results
                        assert 'search_source' in search_data, "Search response should include source"
                        assert 'results' in search_data, "Search response should include results"
                        assert len(search_data['results']) > 0, "Should return at least one search result"
                        search_completed = True
                        break
        
        assert search_completed, "Search did not complete successfully"
        
        print("\n🎉 All MCP protocol tests passed!")
        
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Server not available: {e}")
    except json.JSONDecodeError as e:
        pytest.fail(f"JSON parsing failed: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

def check_server_health():
    """Check if the MCP server is running."""
    try:
        response = requests.get("http://localhost:8000/mcp/", timeout=2)
        print(f"✅ Server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException:
        print("❌ Server is not running on port 8000")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test MCP SSE protocol')
    parser.add_argument('--check-health', action='store_true',
                        help="Only check if server is running")
    args = parser.parse_args()
    
    if args.check_health:
        check_server_health()
    else:
        if not check_server_health():
            print("\n💡 Start the server first:")
            print("   docker run -d -p 8000:8000 tmfrisinger/webcat:latest")
            exit(1)
        
        # Run the pytest test directly
        import subprocess
        result = subprocess.run(['python', '-m', 'pytest', __file__ + '::test_mcp_protocol', '-v'], 
                              capture_output=False)
        exit(result.returncode) 