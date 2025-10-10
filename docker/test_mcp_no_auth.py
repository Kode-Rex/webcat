# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Test MCP server without auth - verify max_results parameter works."""

import json

import requests

base_url = "http://localhost:8000/mcp"  # nginx proxy

# Create session with required headers
session = requests.Session()
session.headers.update({"Accept": "application/json, text/event-stream"})

# Step 1: Initialize
print("1. Initializing MCP session...")
init_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
    },
}

init_resp = session.post(base_url, json=init_payload)
print(f"Initialize status: {init_resp.status_code}")

if init_resp.status_code != 200:
    print(f"Initialize failed: {init_resp.text}")
    exit(1)

# Get session ID
session_id = init_resp.headers.get("mcp-session-id")
print(f"Session ID: {session_id}")

if not session_id:
    print("No session ID in response!")
    exit(1)

# Step 2: Send initialized notification
print("\n2. Sending initialized notification...")
initialized_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}

notif_resp = session.post(
    base_url, json=initialized_payload, headers={"mcp-session-id": session_id}
)
print(f"Initialized notification status: {notif_resp.status_code}")

# Step 3: Call search tool with max_results=2
print("\n3. Calling search tool with max_results=2...")
search_payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "search",
        "arguments": {"query": "Model Context Protocol", "max_results": 2},
    },
}

search_resp = session.post(
    base_url, json=search_payload, headers={"mcp-session-id": session_id}, timeout=30
)

print(f"Search status: {search_resp.status_code}")
print("Content-Type:", search_resp.headers.get("content-type"))
print("\nResponse (first 2000 chars):")
print(search_resp.text[:2000])

# Parse SSE response
if search_resp.status_code == 200:
    # Extract JSON from SSE format
    lines = search_resp.text.strip().split("\n")
    for line in lines:
        if line.startswith("data: "):
            data_json = line[6:]  # Remove "data: " prefix
            result = json.loads(data_json)

            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    # Parse the JSON string inside text
                    search_result = json.loads(text_content)

                    result_count = len(search_result.get("results", []))
                    print(f"\n✅ Found {result_count} results (expected 2)")
                    print(f"Search source: {search_result.get('search_source')}")

                    for i, res in enumerate(search_result.get("results", []), 1):
                        print(f"\n{i}. {res.get('title')}")
                        print(f"   URL: {res.get('url')}")
                        print(f"   Snippet: {res.get('snippet')[:100]}...")

                    if result_count == 2:
                        print("\n✅ max_results parameter works correctly!")
                    else:
                        print(f"\n⚠️  Expected 2 results but got {result_count}")
            break
